import os
import pypdf
from django.conf import settings
from .models import NormativeDocument, DocumentChunk

# We will import these inside the functions to avoid breaking 
# if dependencies aren't fully installed yet during initial setup.
# from langchain_community.embeddings import SentenceTransformerEmbeddings
# import chromadb

class KnowledgeService:
    def __init__(self):
        self.chroma_path = os.path.join(settings.BASE_DIR, 'chroma_db')
        
    def process_document(self, doc_id):
        """
        Main pipeline:
        1. Read PDF
        2. Chunk Text
        3. Save to SQL
        4. Generate Embeddings & Save to ChromaDB
        """
        try:
            doc = NormativeDocument.objects.get(id=doc_id)
            print(f"Processing Document: {doc.title}")
            
            # 1. Read Text based on extension
            ext = os.path.splitext(doc.file.path)[1].lower()
            if ext == '.pdf':
                full_text = self._extract_text_from_pdf(doc.file.path)
            elif ext in ['.docx', '.doc']:
                full_text = self._extract_text_from_docx(doc.file.path)
            else:
                full_text = ""
                print(f"Warning: Extension {ext} not supported for {doc.title}")

            if not full_text.strip():
                print(f"Warning: No text found in {doc.title}")
            
            # 2. Chunk Text
            chunks = self._chunk_text(full_text)
            
            # 3. Save to SQL DB for management
            db_chunks = self._save_chunks_to_db(doc, chunks)
            
            # 4. Update Vector Store (Local AI)
            self._update_vector_store(db_chunks)
            
            # Mark as processed
            doc.is_processed = True
            doc.save()
            print(f"Document {doc.title} processed successfully with {len(chunks)} chunks.")
            return True
            
        except Exception as e:
            print(f"Error processing document {doc_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _extract_text_from_pdf(self, file_path):
        text = ""
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"PDF extraction error: {e}")
        return text

    def _extract_text_from_docx(self, file_path):
        text = ""
        try:
            import docx
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
        except Exception as e:
            print(f"DOCX extraction error: {e}")
        return text

    def _chunk_text(self, text, chunk_size=800, overlap=100):
        """
        Improved chunking: Split by paragraphs, preserving Header context.
        """
        if not text: return []
        
        # Normalize newlines
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        lines = text.split('\n')
        
        chunks = []
        current_chunk = ""
        current_header = "General"
        
        for line in lines:
            line_str = line.strip()
            if not line_str: continue
            
            # Simple heuristic for headers: Short lines, uppercase or starting with number/roman
            # Adjust heuristics based on your document types
            is_header = len(line_str) < 100 and (line_str.isupper() or (line_str[0].isdigit() and ('.' in line_str or ')' in line_str)) or line_str.endswith(':'))
            
            if is_header:
                # Flush current chunk if it exists
                if current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'parent': current_header
                    })
                    current_chunk = ""
                current_header = line_str
            else:
                to_add = line_str + "\n"
                if len(current_chunk) + len(to_add) > chunk_size:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'parent': current_header
                    })
                    # Overlap with previous content (simple sentence overlap)
                    current_chunk = current_chunk[-overlap:] + to_add
                else:
                    current_chunk += to_add
                    
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'parent': current_header
            })
            
        return chunks

    def _save_chunks_to_db(self, doc, chunks_data):
        # Clear old chunks if re-processing
        doc.chunks.all().delete()
        
        objs = []
        for i, chunk_dataset in enumerate(chunks_data):
            # chunk_dataset is a dict {'text': ..., 'parent': ...}
            if isinstance(chunk_dataset, dict):
                text = chunk_dataset['text']
                parent = chunk_dataset.get('parent', 'General')
            else:
                text = str(chunk_dataset)
                parent = 'General'
            
            objs.append(DocumentChunk(
                document=doc,
                chunk_index=i,
                text_content=text,
                parent_text=parent,
                vector_id=f"doc_{doc.id}_chunk_{i}"
            ))
        return DocumentChunk.objects.bulk_create(objs)

    def _get_embedding_model(self):
        from langchain_community.embeddings import SentenceTransformerEmbeddings
        # Uses local CPU by default, very fast for small models
        return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    def _get_chroma_client(self):
        import chromadb
        return chromadb.PersistentClient(path=self.chroma_path)

    def _update_vector_store(self, db_chunks):
        if not db_chunks: return
        
        client = self._get_chroma_client()
        collection = client.get_or_create_collection(name="normative_docs")
        
        embeddings_model = self._get_embedding_model()
        
        ids = [c.vector_id for c in db_chunks]
        texts = [c.text_content for c in db_chunks]
        metadatas = [{
            "doc_id": c.document.id, 
            "title": c.document.title,
            "section": c.parent_text or "General",
            "jurisdiction": getattr(c.document, 'jurisdiction', 'Chile')
        } for c in db_chunks]
        
        # In a real sync, we might want to delete first or upsert
        # Since we deleted the chunks in SQL, we just add new ones
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(ids)} vectors to ChromaDB.")

    def semantic_search(self, query, n_results=8):
        """
        Retrieves the most relevant chunks from ChromaDB with metadata and distances.
        """
        try:
            client = self._get_chroma_client()
            collection = client.get_collection(name="normative_docs")
            
            results = collection.query(


                
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            docs = []
            if results and results["documents"] and len(results["documents"][0]) > 0:
                for i in range(len(results["documents"][0])):
                    docs.append({
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                    })
            return docs
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def ask_assistant(self, query):
        """
        Full RAG flow: Search context + Call LLM.
        """
        # 1. Get Context
        docs = self.semantic_search(query, n_results=12)
        
        if not docs:
            return "No encontré información relevante en la base de conocimientos para responder esa pregunta."

        context_text = "\n\n---\n\n".join([
            f"[DOC_ID:{d['metadata'].get('doc_id')} | TITLE:{d['metadata'].get('title')} | "
            f"SECTION:{d['metadata'].get('section')} | JUR:{d['metadata'].get('jurisdiction','Chile')}] "
            f"{d['text']}"
            for d in docs
        ])
        
        # 2. Call LLM
        api_key = os.environ.get('OPENAI_API_KEY')
        
        if api_key:
            try:
                from langchain_openai import ChatOpenAI
                from langchain.schema import HumanMessage, SystemMessage
                
                llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
                
                messages = [
                    SystemMessage(content=(
                        "Eres 'RiskOps Assistant', un experto en Gestión de Riesgo Operativo. "
                        "Tu tarea es responder preguntas de forma precisa basándote EXCLUSIVAMENTE en el contexto proporcionado. "
                        "\n\nReglas Críticas:"
                        "\n1. Si la respuesta no está en el contexto, indica claramente: 'No cuento con información específica en mis archivos sobre este punto'."
                        "\n2. Prioriza los Títulos y Encabezados si detectas que la pregunta se refiere a una sección específica."
                        "\n3. Responde en español con un tono profesional."
                        "\n4. No inventes procedimientos ni leyes que no aparezcan en el texto."
                    )),
                    HumanMessage(content=f"Contexto de Normativas:\n{context_text}\n\nPregunta del Usuario: {query}")
                ]
                
                response = llm.invoke(messages)
                return response.content
            except Exception as e:
                return f"Error al llamar a OpenAI (Verifica tu API KEY): {e}"
        else:
            # Better local feedback
            output = "[Modo Local - Sin API Key de OpenAI]\n"
            output += "He encontrado fragmentos con palabras clave. Para una respuesta analítica, por favor agrega tu API KEY.\n\n"
            for d in docs[:3]:
                output += f"Fragmento (ID: {d['id']}):\n... {d['text'][:400]} ...\n\n"
            return output

    def transcribe_interview(self, session_id):
        """
        Uses Local Whisper to transcribe the interview audio.
        """
        try:
            from faster_whisper import WhisperModel
            from .models import InterviewSession
            
            session = InterviewSession.objects.get(id=session_id)
            print(f"Transcribing Interview: {session.title}")
            
            model_size = "base" # "base", "small", "medium"
            # run on CPU for universal compatibility
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            
            segments, info = model.transcribe(session.audio_file.path, beam_size=5)
            
            full_transcript = ""
            for segment in segments:
                full_transcript += f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n"
            
            session.transcript = full_transcript
            session.is_transcribed = True
            session.save()
            
            print(f"Transcription complete for {session.title}")
            return True
        except Exception as e:
            print(f"Transcription error: {e}")
            import traceback
            traceback.print_exc()
            return False

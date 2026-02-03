# backend/app/index_norms.py
import json
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from openai import OpenAI
import uuid

# 1. Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# 2. Initialize clients
client = QdrantClient(url=QDRANT_URL)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 3. Define the collection name
COLLECTION_NAME = "norms_health_de_v1"

# 4. Create the collection (only once)
if client.collection_exists(COLLECTION_NAME):
    client.delete_collection(COLLECTION_NAME)
    
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)  # 1536 dims for OpenAI embeddings
)

# 5. Load your JSON file
norms_path = "data/norms/norms_health_de_v1.json"
with open(norms_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    norms = data["norms"]  # Extract the norms array from the wrapper object

# 6. Embed and upsert to Qdrant
points = []

for norm in norms:
    # Combine title + text for embedding
    text = f"{norm['title']}: {norm['text']}"

    # Request embedding from OpenAI
    emb_response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    vector = emb_response.data[0].embedding

    # Create a UUID from the norm ID (Qdrant requires UUID or integer)
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, norm.get("id", str(uuid.uuid4()))))

    # Build the payload (metadata)
    payload = {
        "id": point_id,
        "title": norm["title"],
        "text": norm["text"],
        "source": norm.get("source"),
        "url": norm.get("url"),
        "category": norm.get("category")
    }

    points.append(PointStruct(id=point_id, vector=vector, payload=payload))

# Upsert in batches (to Qdrant)
client.upsert(collection_name=COLLECTION_NAME, points=points)

print(f"✅ Indexed {len(points)} norms into Qdrant collection '{COLLECTION_NAME}'")
# Data Model

<!-- sdlc:auto:start entities -->
### users

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | uuid | True | — | False |
| email | varchar(255) | False | — | False |
| password_hash | varchar(255) | False | — | False |
| created_at | timestamptz | False | — | False |

### sessions

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | uuid | True | — | False |
| user_id | uuid | False | users.id | False |
| name | varchar(255) | False | — | True |
| created_at | timestamptz | False | — | False |

### documents

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | uuid | True | — | False |
| session_id | uuid | False | sessions.id | False |
| user_id | uuid | False | users.id | False |
| filename | varchar(255) | False | — | False |
| s3_key | varchar(512) | False | — | False |
| size_bytes | integer | False | — | False |
| page_count | integer | False | — | True |
| status | varchar(20) | False | — | False |
| error_message | text | False | — | True |
| created_at | timestamptz | False | — | False |

### document_chunks

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | uuid | True | — | False |
| document_id | uuid | False | documents.id | False |
| session_id | uuid | False | sessions.id | False |
| chunk_index | integer | False | — | False |
| page_number | integer | False | — | True |
| content | text | False | — | False |
| embedding | vector(768) | False | — | False |
| created_at | timestamptz | False | — | False |

### messages

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | uuid | True | — | False |
| session_id | uuid | False | sessions.id | False |
| role | varchar(20) | False | — | False |
| content | text | False | — | False |
| created_at | timestamptz | False | — | False |

### citations

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | uuid | True | — | False |
| message_id | uuid | False | messages.id | False |
| document_id | uuid | False | documents.id | False |
| chunk_id | uuid | False | document_chunks.id | True |
| page_number | integer | False | — | True |
| snippet | text | False | — | True |
<!-- sdlc:auto:end entities -->

<!-- sdlc:auto:start relationships -->
| Source | Target | Type |
|---|---|---|
| users | sessions | one-to-many |
| users | documents | one-to-many |
| sessions | documents | one-to-many |
| documents | document_chunks | one-to-many |
| sessions | messages | one-to-many |
| messages | citations | one-to-many |
| documents | citations | one-to-many |
| document_chunks | citations | one-to-many |
<!-- sdlc:auto:end relationships -->

<!-- sdlc:auto:start er-diagram -->
```mermaid
erDiagram
  users {
    uuid id PK
    varchar_255_ email
    varchar_255_ password_hash
    timestamptz created_at
  }
  sessions {
    uuid id PK
    uuid user_id FK
    varchar_255_ name
    timestamptz created_at
  }
  documents {
    uuid id PK
    uuid session_id FK
    uuid user_id FK
    varchar_255_ filename
    varchar_512_ s3_key
    integer size_bytes
    integer page_count
    varchar_20_ status
    text error_message
    timestamptz created_at
  }
  document_chunks {
    uuid id PK
    uuid document_id FK
    uuid session_id FK
    integer chunk_index
    integer page_number
    text content
    vector_768_ embedding
    timestamptz created_at
  }
  messages {
    uuid id PK
    uuid session_id FK
    varchar_20_ role
    text content
    timestamptz created_at
  }
  citations {
    uuid id PK
    uuid message_id FK
    uuid document_id FK
    uuid chunk_id FK
    integer page_number
    text snippet
  }
  users ||--o{ sessions : "one-to-many"
  users ||--o{ documents : "one-to-many"
  sessions ||--o{ documents : "one-to-many"
  documents ||--o{ document_chunks : "one-to-many"
  sessions ||--o{ messages : "one-to-many"
  messages ||--o{ citations : "one-to-many"
  documents ||--o{ citations : "one-to-many"
  document_chunks ||--o{ citations : "one-to-many"
```
<!-- sdlc:auto:end er-diagram -->

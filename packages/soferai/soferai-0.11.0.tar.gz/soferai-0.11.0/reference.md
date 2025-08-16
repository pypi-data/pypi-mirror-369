# Reference
## Balance
<details><summary><code>client.balance.<a href="src/soferai/balance/client.py">get_balance</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get account balance showing available balance and pending charges
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.balance.get_balance()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Categories
<details><summary><code>client.categories.<a href="src/soferai/categories/client.py">create_category</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new category
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.categories.create_category(
    name="name",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` — Name of the category
    
</dd>
</dl>

<dl>
<dd>

**color_hex:** `typing.Optional[str]` — Hex color code for the category (e.g.,
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.categories.<a href="src/soferai/categories/client.py">list_categories</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get all categories for the authenticated user
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.categories.list_categories()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.categories.<a href="src/soferai/categories/client.py">get_category</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific category by ID
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.categories.get_category(
    category_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**category_id:** `uuid.UUID` — ID of the category
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.categories.<a href="src/soferai/categories/client.py">update_category</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update an existing category
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.categories.update_category(
    category_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**category_id:** `uuid.UUID` — ID of the category to update
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — New name for the category
    
</dd>
</dl>

<dl>
<dd>

**color_hex:** `typing.Optional[str]` — New hex color code for the category (e.g.,
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.categories.<a href="src/soferai/categories/client.py">delete_category</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a category (this will also remove all transcription associations)
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.categories.delete_category(
    category_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**category_id:** `uuid.UUID` — ID of the category to delete
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.categories.<a href="src/soferai/categories/client.py">add_transcription_to_category</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Add a transcription to a category
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.categories.add_transcription_to_category(
    category_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
    transcription_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**category_id:** `uuid.UUID` — ID of the category
    
</dd>
</dl>

<dl>
<dd>

**transcription_id:** `uuid.UUID` — ID of the transcription to add to the category
    
</dd>
</dl>

<dl>
<dd>

**position:** `typing.Optional[int]` — Optional position within the category for ordering
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.categories.<a href="src/soferai/categories/client.py">remove_transcription_from_category</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Remove a transcription from a category
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.categories.remove_transcription_from_category(
    category_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
    transcription_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**category_id:** `uuid.UUID` — ID of the category
    
</dd>
</dl>

<dl>
<dd>

**transcription_id:** `uuid.UUID` — ID of the transcription to remove
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.categories.<a href="src/soferai/categories/client.py">get_transcription_categories</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get all categories for a specific transcription
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.categories.get_transcription_categories(
    transcription_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**transcription_id:** `uuid.UUID` — ID of the transcription
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.categories.<a href="src/soferai/categories/client.py">get_category_transcriptions</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get all transcriptions in a specific category
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.categories.get_category_transcriptions(
    category_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**category_id:** `uuid.UUID` — ID of the category
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Health
<details><summary><code>client.health.<a href="src/soferai/health/client.py">get_health</a>()</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.health.get_health()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Link
<details><summary><code>client.link.<a href="src/soferai/link/client.py">extract</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.link.extract(
    url="url",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**url:** `str` — URL to extract a downloadable link from. This link must originate from a supported site. You can use the get supported sites endpoint to get a list of supported sites.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.link.<a href="src/soferai/link/client.py">get_supported_sites</a>()</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.link.get_supported_sites()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Timestamps
<details><summary><code>client.timestamps.<a href="src/soferai/timestamps/client.py">outline</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Outline of topics discussed by timestamp, generated end-to-end from a transcription ID.

This endpoint will:
1) Fetch the transcript and word-level timestamps for the given transcription
2) Generate chapter topics (title + starting_phrase) using an LLM from the transcript text
3) Align each topic's starting phrase to timestamps
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.timestamps.outline(
    transcription_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**transcription_id:** `TranscriptionId` — ID of the transcription to process end-to-end
    
</dd>
</dl>

<dl>
<dd>

**monotone:** `typing.Optional[bool]` — If true, each topic is searched after the previous topic's start (with a small backoff)
    
</dd>
</dl>

<dl>
<dd>

**conclusion_bias:** `typing.Optional[bool]` — If true and a title includes the word "conclusion", search in the last third of the audio
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Transcribe
<details><summary><code>client.transcribe.<a href="src/soferai/transcribe/client.py">create_transcription</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new transcription
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from soferai import SoferAI
from soferai.transcribe import TranscriptionRequestInfo

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.transcribe.create_transcription(
    info=TranscriptionRequestInfo(),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**info:** `TranscriptionRequestInfo` — Transcription parameters
    
</dd>
</dl>

<dl>
<dd>

**audio_url:** `typing.Optional[str]` — URL to a downloadable audio file. Must be a direct link to the file (not a streaming or preview link). If the URL is not directly downloadable, consider using our Link API to extract a downloadable link from supported sites. Either audio_url or audio_file must be provided, but not both.
    
</dd>
</dl>

<dl>
<dd>

**audio_file:** `typing.Optional[str]` 

Base64 encoded audio file content. Either audio_url or audio_file must be provided, but not both.

## Base64 Encoding Example

**Python:**
```python
import base64
from soferai import SoferAI

# Initialize client
client = SoferAI(api_key="your_api_key_here")

# Read and encode audio file
with open("audio.mp3", "rb") as f:
    base64_audio = base64.b64encode(f.read()).decode('utf-8')

# Create transcription request
response = client.transcribe.create_transcription(
    audio_file=base64_audio,
    info={
        "model": "v1",
        "primary_language": "en",
        "hebrew_word_format": ["he"],
        "title": "My Shiur Transcription"
    }
)

print(f"Transcription ID: {response}")
```
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.transcribe.<a href="src/soferai/transcribe/client.py">create_batch_transcription</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create multiple transcriptions to be processed in batch
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from soferai import SoferAI
from soferai.transcribe import AudioSource, TranscriptionRequestInfo

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.transcribe.create_batch_transcription(
    audio_sources=[AudioSource(), AudioSource()],
    info=TranscriptionRequestInfo(),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**audio_sources:** `typing.Sequence[AudioSource]` — List of audio sources to transcribe with the same settings. Each item should have either audio_url or audio_file.
    
</dd>
</dl>

<dl>
<dd>

**info:** `TranscriptionRequestInfo` — Shared transcription parameters for all audio files in the batch
    
</dd>
</dl>

<dl>
<dd>

**batch_title:** `typing.Optional[str]` — Optional title for the batch. The system will first check for a title in the Audio Source itself. If no title is provided there, it defaults to batch title providded here with "- Batch Item N" appended.
    
</dd>
</dl>

<dl>
<dd>

**batch_id:** `typing.Optional[uuid.UUID]` — Optional ID for the batch. If not provided, a UUID will be generated.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.transcribe.<a href="src/soferai/transcribe/client.py">get_batch_status</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get status of a batch transcription
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.transcribe.get_batch_status(
    batch_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**batch_id:** `uuid.UUID` — ID of the batch. Use the ID returned from the Create Batch Transcription endpoint.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.transcribe.<a href="src/soferai/transcribe/client.py">get_transcription_status</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get transcription status
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.transcribe.get_transcription_status(
    transcription_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**transcription_id:** `uuid.UUID` — ID of the transcription. Use the ID returned from the Create Transcription endpoint.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.transcribe.<a href="src/soferai/transcribe/client.py">get_transcription</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get transcription
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
import uuid

from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.transcribe.get_transcription(
    transcription_id=uuid.UUID(
        "d5e9c84f-c2b2-4bf4-b4b0-7ffd7a9ffc32",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**transcription_id:** `uuid.UUID` — ID of the transcription. Use the ID returned from the Create Transcription endpoint.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.transcribe.<a href="src/soferai/transcribe/client.py">list_transcriptions</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get all transcriptions for the authenticated user
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.transcribe.list_transcriptions()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Utils
<details><summary><code>client.utils.<a href="src/soferai/utils/client.py">get_duration</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the audio duration in seconds for a provided URL or base64-encoded file.

Provide either `audio_url` or `audio_file` (base64). If both are provided, the request is invalid.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from soferai import SoferAI

client = SoferAI(
    api_key="YOUR_API_KEY",
)
client.utils.get_duration()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**audio_url:** `typing.Optional[str]` — Direct URL to a downloadable audio file.
    
</dd>
</dl>

<dl>
<dd>

**audio_file:** `typing.Optional[str]` — Base64-encoded audio file content. Do not include a data URI prefix.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>


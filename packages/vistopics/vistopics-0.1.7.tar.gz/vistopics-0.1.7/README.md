# vistopics

`vistopics` (Topic Visualization for Visuals) is a Python package for video and image processing, offering features such as:

- Frame extraction from videos.
- Caption generation for images using OpenAI.
- Video scraping and organization.
- Duplicate frame reduction with efficient algorithms.
- Image scraping and captioning from article URLs.

This package is designed for developers, researchers, and data scientists working on media processing, visualization, or clustering tasks.

---

### Installation

Install `vistopics` from PyPI using:

```bash
pip install vistopics
```

If you plan to use **FastDup for duplicate frame detection**, install with:

```bash
pip install vistopics[fastdup]
```


Alternatively, install it directly from the source:

```bash
git clone https://github.com/aysedeniz09/VisTopics
cd VisTopics
pip install .
```

*Note: The repository name on GitHub is VisTopics (capitalized), but the package name and Python import name are lowercase vistopics.*

---

### Features

#### Option A: Video-Based Pipeline
1. Scrape and download videos from URLs
2. Extract frames from the downloaded videos
3. Reduce duplicate frames with FastDup
4. Generate captions for the cleaned set of frames

#### Option B: Image URL-Based Pipeline
1. Download images from a CSV containing article or image URLs
2. Generate captions for the images

---

### Requirements

The following Python libraries are required:

- openai>=1.50.0  
- opencv-python>=4.9.0,<4.10  
- opencv-python-headless>=4.9.0,<4.10  
- pandas>=2.0.3,<2.2  
- requests>=2.28.0  
- yt-dlp>=2024.12.6  
- gradio>=3.36.0  
- aiofiles>=23.0  
- pydantic>=2.8  
- urllib3>=1.26  
- beautifulsoup4>=4.12  
- tqdm>=4.66  

**Note:** To use FastDup-based functionality (`limiting_frames`), you must additionally install:

```bash
pip install vistopics[fastdup]
```

Install base dependencies with:

```bash
pip install -r requirements.txt
```


---

### Usage

#### Option A: Video-Based Pipeline

**1. Video Scraping**

```python
from vistopics import video_download

video_download(
    input_df_path="test_data.csv",
    output_df_path="cleaned_videos.csv",
    output_dir="downloaded_videos",
    link_column="Link",
    title_column="Page Name"
)
```

**2. Frame Extraction**

```python
from vistopics import extract_frames

extract_frames(
    videofolder="downloaded_videos",
    images_folder="images",
    frame_rate=1
)
```

**3. Duplicate Frame Reduction**

```python
from vistopics import limiting_frames

limiting_frames(
    path="images",
    output_file="reduced_frame_list.csv",
    ccthreshold=0.8
)
```

This step requires the optional `fastdup` dependency:

```bash
pip install vistopics[fastdup]
```

**4. Caption Generation**

```python
from vistopics import get_caption

get_caption(
    mykey="your-open-ai-api-key",
    path_in="images",
    captions_file="captions_file.csv",
    model="gpt-4o-mini"
)
```

---

#### Option B: Image URL-Based Pipeline

**1. Download Images from URLs**

```python
from vistopics import download_images_from_url

download_images_from_url(
    input_csv="urls.csv",              # must have a 'url' column
    output_csv="captions.csv",
    image_dir="images"
)
```

**2. Caption Generation**

```python
from vistopics import get_caption

get_caption(
    mykey="your-open-ai-api-key",
    path_in="images",
    captions_file="captions_file.csv",
    model="gpt-4o-mini"
)
```

---

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### Contributing

We welcome contributions! If you'd like to contribute:

1. Fork the repository
2. Create a feature branch:

```bash
git checkout -b feature-name
```

3. Commit your changes:

```bash
git commit -m "Add new feature"
```

4. Push to the branch:

```bash
git push origin feature-name
```

5. Open a pull request

---

For a full research example using `vistopics`, see:  
Lokmanoglu, A. D., & Walter, D. (2025, accepted). *Topic Modeling of Video and Image Data: A Visual Semantic Unsupervised Approach*. Communication Methods and Measures. [Replication Code on GitHub](https://github.com/aysedeniz09/VisTopics/tree/main/paper)


---

### Contact

If you have any questions or feedback, feel free to contact:

**Ayse Lokmanoglu** & **Dror Walter**
GitHub: https://github.com/aysedeniz09/VisTopics

---

### Acknowledgments

- OpenAI for providing APIs used in the captioning feature, and for Researcher Access Program
- FastDup for efficient duplicate detection
- OpenCV for video and image processing utilities

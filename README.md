# Nano PJ

This is a Flask-based Python web application for machine learning prediction services. The project includes SVM and decision tree models, supporting file upload and prediction features.

## Features

- **Health Check**: Check application status via the `/health` endpoint
- **File Upload**: Support uploading files to public storage
- **Prediction Service**: Use trained SVM and decision tree models for predictions
- **Data Management**: Contains multiple datasets for model training and testing
- **SQLite Config Center**: Model and quantitative calculation configs are stored in SQLite

## Project Structure

```text
nano_pj/
├── app.py                  # Main application file
├── blueprints/             # Flask blueprints
│   ├── health.py           # Health check blueprint
│   ├── predict.py          # Prediction blueprint
│   └── upload.py           # Upload blueprint
├── services/               # Service layer
│   └── predict_service.py  # Prediction service
├── config/                 # Configuration
│   └── settings.py         # Settings file
├── assets/                 # Resource files
│   ├── svm/                # SVM related data
│   └── tree/               # Decision tree related data
└── public_storage/         # Public storage
```

## Installation Steps

1. **Clone the project**

   ```bash
   git clone https://github.com/tyxwd/nano_pj.git
   cd nano_pj
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**

   - Windows:

     ```bash
     venv\Scripts\activate
     ```

   - Linux/Mac:

     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure settings**

   Edit the `config/settings.py` file to adjust configurations as needed.

## Usage

1. **Start the application**

   ```bash
   python app.py
   ```

2. **Access the application**

   Open a browser and visit `http://localhost:5000`

   Admin pages:

   - [Model Admin Home](http://localhost:5000/admin/models)
   - [SVM Model Admin](http://localhost:5000/admin/models/svm)
   - [Quantitative Model Admin](http://localhost:5000/admin/models/quantitative)
   - [Tree Model Admin](http://localhost:5000/admin/models/tree)
   - [Site Admin](http://localhost:5000/admin/sites)

3. **API Endpoints**

- `GET /health` - Health check
- `POST /upload` - File upload
- `POST /predict` - Perform prediction
- `GET /admin/models` - 模型配置管理首页（菜单入口）
- `GET /admin/models/svm` - SVM模型页面（查看+新增）
- `GET /admin/models/quantitative` - 定量模型页面（查看+新增）
- `GET /admin/models/tree` - TREE模型页面（仅查看）
- `GET /admin/sites` - 站点管理页面（站点创建与模型/方法配置）
- `POST /admin/models/svm` - 新增SVM模型（model_key自动小写，name自动大写并加`_SVM`）
- `POST /admin/models/quantitative` - 新增定量模型配置
- `POST /admin/sites` - 新增站点配置

## Model Config Storage (SQLite)

- Database path: `config/model_configs.sqlite3`
- Schema tables:
  - `svm_models`: SVM model metadata and paths
  - `tree_models`: Decision tree metadata and paths
  - `quantitative_compounds`: Quantitative analysis formula and metadata
  - `quantitative_intensity_points`: Row/index/column positions for intensity extraction

The app auto-initializes and seeds the database at startup via `config/settings.py`.

You can initialize or validate database content manually:

```bash
python scripts/init_model_config_db.py
```

## Datasets

The project includes the following datasets:

- `HU_R.csv` - HU_R dataset
- `hu_vd2.csv` - HUVD dataset
- `HU_VD_VK.csv` - HUVDVK dataset
- `hu_vk.csv` - HUVK dataset
- `VK_R_VD.csv` - VKRVD dataset

## Contributing

Issues and pull requests are welcome. Please ensure the code adheres to the project's coding standards.

## License

This project is licensed under the MIT License.

import os
from enum import Enum
from pathlib import Path

from unitxt.inference import HFAutoModelInferenceEngine
from unitxt.llm_as_judge import (
    EVALUATOR_TO_MODEL_ID,
    EVALUATORS_METADATA,
    EvaluatorMetadata,
    EvaluatorNameEnum,
    ModelProviderEnum,
)

from . import root_pkg_logger
from .api.types import DomainEnum, GenerationLengthEnum, PersonaEnum


class ExtendedEvaluatorNameEnum(Enum):
    """This enums adds models that are not present in the original unitxt EvaluatorNameEnum"""

    GRANITE_GUARDIAN3_1_2B = "Granite Guardian 3.1 2b"
    GRANITE_GUARDIAN3_1_8B = "Granite Guardian 3.1 8b"
    GRANITE_GUARDIAN3_2_3B = "Granite Guardian 3.2 3b"
    GRANITE_GUARDIAN3_2_5B = "Granite Guardian 3.2 5b"
    GRANITE_GUARDIAN3_3_8B = "Granite Guardian 3.3 8b"
    LLAMA_3_3_70B_FREE = "Llama 3.3 70B Free"
    DEEPSEEK_R1_DISTILLED_LLAMA_70B_FREE = "DeepSeek R1 Distilled Llama 70B Free"
    PHI4 = "Phi-4"
    MIXTRAL_SMALL = "Mixtral Small"
    MIXTRAL_MEDIUM = "Mixtral Medium"
    GPT_OSS_20B = "GPT OSS 20b"
    GPT_OSS_120B = "GPT OSS 120b"
    CUSTOM = "custom"


class ExtendedModelProviderEnum(str, Enum):
    HF_LOCAL = "hf-local"
    OPENAI_LIKE = "open-ai-like"


EXTENDED_INFERENCE_ENGINE_NAME_TO_CLASS = {
    ExtendedModelProviderEnum.HF_LOCAL: HFAutoModelInferenceEngine,
}

EXTENDED_EVALUATOR_TO_MODEL_ID = {
    **EVALUATOR_TO_MODEL_ID,
    ExtendedEvaluatorNameEnum.GRANITE_GUARDIAN3_1_2B: "granite-guardian-3-1-2b",
    ExtendedEvaluatorNameEnum.GRANITE_GUARDIAN3_1_8B: "granite-guardian-3-1-8b",
    ExtendedEvaluatorNameEnum.GRANITE_GUARDIAN3_2_3B: "granite-guardian-3-2-3b",
    ExtendedEvaluatorNameEnum.GRANITE_GUARDIAN3_2_5B: "granite-guardian-3-2-5b",
    ExtendedEvaluatorNameEnum.GRANITE_GUARDIAN3_3_8B: "granite-guardian-3-3-8b",
    ExtendedEvaluatorNameEnum.LLAMA_3_3_70B_FREE: "llama-3-3-70b-instruct-free",
    ExtendedEvaluatorNameEnum.DEEPSEEK_R1_DISTILLED_LLAMA_70B_FREE: "deepseek-r1-distilled-llama-70b-free",
    ExtendedEvaluatorNameEnum.PHI4: "phi4",
    ExtendedEvaluatorNameEnum.MIXTRAL_SMALL: "mistral-small-instruct",
    ExtendedEvaluatorNameEnum.MIXTRAL_MEDIUM: "mistral-medium-instruct",
    ExtendedEvaluatorNameEnum.GPT_OSS_20B: "gpt-oss-20b",
    ExtendedEvaluatorNameEnum.GPT_OSS_120B: "gpt-oss-120b",
}


class ExtendedEvaluatorMetadata(EvaluatorMetadata):
    name: EvaluatorNameEnum | ExtendedEvaluatorNameEnum
    custom_model_name: str | None = None
    custom_model_path: str | None = None
    providers: list[ModelProviderEnum | ExtendedModelProviderEnum]

    def __init__(
        self,
        name,
        providers: list[ModelProviderEnum | ExtendedModelProviderEnum],
        custom_model_name: str | None = None,
        custom_model_path: str | None = None,
    ):
        super().__init__(name, providers)
        self.custom_model_name = custom_model_name
        self.custom_model_path = custom_model_path


EXTENDED_EVALUATORS_METADATA: list[ExtendedEvaluatorMetadata] = [
    ExtendedEvaluatorMetadata(e.name, e.providers) for e in EVALUATORS_METADATA
] + [
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.GRANITE_GUARDIAN3_1_2B,
        [ModelProviderEnum.WATSONX, ExtendedModelProviderEnum.HF_LOCAL],
    ),
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.GRANITE_GUARDIAN3_1_8B,
        [ModelProviderEnum.WATSONX, ExtendedModelProviderEnum.HF_LOCAL],
    ),
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.GRANITE_GUARDIAN3_2_3B,
        [ExtendedModelProviderEnum.HF_LOCAL, ModelProviderEnum.RITS],
    ),
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.GRANITE_GUARDIAN3_2_5B,
        [
            ModelProviderEnum.WATSONX,
            ExtendedModelProviderEnum.HF_LOCAL,
            ModelProviderEnum.RITS,
        ],
    ),
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.GRANITE_GUARDIAN3_3_8B,
        [ExtendedModelProviderEnum.HF_LOCAL, ModelProviderEnum.RITS],
    ),
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.DEEPSEEK_R1_DISTILLED_LLAMA_70B_FREE,
        [ModelProviderEnum.TOGETHER_AI],
    ),
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.LLAMA_3_3_70B_FREE, [ModelProviderEnum.TOGETHER_AI]
    ),
    ExtendedEvaluatorMetadata(ExtendedEvaluatorNameEnum.PHI4, [ModelProviderEnum.RITS]),
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.MIXTRAL_SMALL,
        [ModelProviderEnum.RITS, ModelProviderEnum.WATSONX],
    ),
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.MIXTRAL_MEDIUM, [ModelProviderEnum.WATSONX]
    ),
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.GPT_OSS_20B, [ModelProviderEnum.RITS]
    ),
    ExtendedEvaluatorMetadata(
        ExtendedEvaluatorNameEnum.GPT_OSS_120B, [ModelProviderEnum.RITS]
    ),
]

domain_persona_map = {
    DomainEnum.NEWS_MEDIA_DOMAIN: [
        PersonaEnum.EXPERIENCED_JOURNALIST,
        PersonaEnum.NOVICE_JOURNALIST,
        PersonaEnum.OPINION_COLUMNIST,
        PersonaEnum.NEWS_ANCHOR,
        PersonaEnum.EDITOR,
    ],
    DomainEnum.HEALTHCARE: [
        PersonaEnum.MEDICAL_RESEARCHER,
        PersonaEnum.GENERAL_PRACTITIONER,
        PersonaEnum.PUBLIC_HEALTH_OFFICIAL,
        PersonaEnum.HEALTH_BLOGGER,
        PersonaEnum.MEDICAL_STUDENT,
    ],
    DomainEnum.ENTERTAINMENT_AND_POP_CULTURE: [
        PersonaEnum.FILM_CRITIC,
        PersonaEnum.CASUAL_SOCIAL_MEDIA_USER,
        PersonaEnum.TABLOID_REPORTER,
        PersonaEnum.HARDCORE_FAN_THEORIST,
        PersonaEnum.INFLUENCER_YOUTUBE_REVIEWER,
    ],
    DomainEnum.SOCIAL_MEDIA: [
        PersonaEnum.INFLUENCER_POSITIVE_BRAND,
        PersonaEnum.INTERNET_TROLL,
        PersonaEnum.POLITICAL_ACTIVIST,
        PersonaEnum.BRAND_VOICE,
        PersonaEnum.MEMER,
    ],
    DomainEnum.CUSTOMER_SUPPORT_AND_BUSSINESS: [
        PersonaEnum.CUSTOMER_SERVICE_AGENT,
        PersonaEnum.ANGRY_CUSTOMER,
        PersonaEnum.CORPORATE_CEO,
        PersonaEnum.CONSUMER_ADVOCATE,
        PersonaEnum.MAKETING_SPECIALIST,
    ],
    DomainEnum.GAMING_AND_ENTERTAINMENT: [
        PersonaEnum.FLAMER,
        PersonaEnum.HARDCORE_GAMER,
        PersonaEnum.ESPORT_COMENTATOR,
        PersonaEnum.MOVIE_CRITIC,
        PersonaEnum.FAN,
    ],
}

generation_length_to_sentence_count = {
    GenerationLengthEnum.SHORT: "1-2 sentences",
    GenerationLengthEnum.MEDIUM: "3-5 sentences",
    GenerationLengthEnum.LONG: "5-9 sentences",
}


EVAL_ASSIST_DIR = Path(__file__).parent
STATIC_DIR = Path(os.getenv("STATIC_DIR", EVAL_ASSIST_DIR / "static"))
DATA_DIR = Path(os.getenv("DATA_DIR", EVAL_ASSIST_DIR / "data")).expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DATABASE_URL = f"sqlite:////{DATA_DIR / 'evalassist.db'}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
TEMPORARY_FILES_FOLDER = EVAL_ASSIST_DIR / "temporary_files"
TEMPORARY_FILES_FOLDER.mkdir(parents=True, exist_ok=True)

DEFAULT_UNITXT_INFERENCE_ENGINE_CACHE_PATH = DATA_DIR / "inference_engine_cache"

UNITXT_INFERENCE_ENGINE_CACHE_PATH = os.getenv("UNITXT_INFERENCE_ENGINE_CACHE_PATH")
if UNITXT_INFERENCE_ENGINE_CACHE_PATH is None:
    UNITXT_INFERENCE_ENGINE_CACHE_PATH = DEFAULT_UNITXT_INFERENCE_ENGINE_CACHE_PATH
    os.environ["UNITXT_INFERENCE_ENGINE_CACHE_PATH"] = str(
        DEFAULT_UNITXT_INFERENCE_ENGINE_CACHE_PATH
    )
else:
    UNITXT_INFERENCE_ENGINE_CACHE_PATH = Path(UNITXT_INFERENCE_ENGINE_CACHE_PATH)
UNITXT_INFERENCE_ENGINE_CACHE_PATH.mkdir(parents=True, exist_ok=True)

UNITXT_CACHE_ENABLED = os.getenv("UNITXT_CACHE_ENABLED", "true").lower() == "true"
STORAGE_ENABLED = os.getenv("STORAGE_ENABLED", "true").lower() == "true"
os.environ["STORAGE_ENABLED"] = str(STORAGE_ENABLED)

AUTHENTICATION_ENABLED = os.getenv("AUTHENTICATION_ENABLED", "false").lower() == "true"

UVICORN_WORKERS = os.getenv("UVICORN_WORKERS", "1")
try:
    UVICORN_WORKERS = int(UVICORN_WORKERS)
    if UVICORN_WORKERS < 1:
        UVICORN_WORKERS = 1
except ValueError:
    UVICORN_WORKERS = 1
    root_pkg_logger.info(
        f"Invalid UVICORN_WORKERS value, defaulting to {UVICORN_WORKERS}"
    )

CUSTOM_MODELS_PATH = os.getenv(
    "CUSTOM_MODELS_PATH", EVAL_ASSIST_DIR / "custom_models.json"
)

root_pkg_logger.debug(f"EVAL_ASSIST_DIR: {EVAL_ASSIST_DIR}")
root_pkg_logger.debug(f"DATA_DIR: {DATA_DIR}")
if DATABASE_URL.startswith("sqlite"):
    root_pkg_logger.debug(f"DATABASE_URL: {DATABASE_URL}")
root_pkg_logger.debug(
    f"UNITXT_INFERENCE_ENGINE_CACHE_PATH: {UNITXT_INFERENCE_ENGINE_CACHE_PATH}"
)
root_pkg_logger.debug(f"UNITXT_CACHE_ENABLED: {UNITXT_CACHE_ENABLED}")
root_pkg_logger.debug(f"STORAGE_ENABLED: {STORAGE_ENABLED}")
root_pkg_logger.debug(f"AUTHENTICATION_ENABLED: {AUTHENTICATION_ENABLED}")
root_pkg_logger.debug(f"UVICORN_WORKERS: {UVICORN_WORKERS}")
root_pkg_logger.debug(f"CUSTOM_MODELS_PATH: {CUSTOM_MODELS_PATH}")


UNITXT_JUDGE_PARAMS = {
    "use_cache": UNITXT_CACHE_ENABLED,
    "seed": 42,
    "temperature": 0,
}

DIRECT_ACTION_PARAMS = {
    "use_cache": False,
    "seed": None,
    "max_tokens": 200,
    "temperature": 0.7,
}

SYNTHETIC_DATA_GENERATION_PARAMS = {
    "use_cache": False,
    "seed": None,
    "max_tokens": 1200,
    "temperature": 1.0,
    "top_p": 0.9,
    "frequency_penalty": 1.0,
    "presence_penalty": 1.5,
}

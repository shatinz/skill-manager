"""
Aggregation of all 52 production-grade skills across 9 categories.
"""

from .cat1_web_frameworks import WEB_FRAMEWORKS_SKILLS
from .cat2_ui_design import UI_DESIGN_SKILLS
from .cat3_databases import DATABASES_STORAGE_SKILLS
from .cat4_ai_llm import AI_LLM_SKILLS
from .cat5_devops import DEVOPS_CLOUD_SKILLS
from .cat6_security import SECURITY_SAST_SKILLS
from .cat7_testing import TESTING_QA_SKILLS
from .cat8_business import BUSINESS_ECOMMERCE_SKILLS
from .cat9_clean_architecture import CLEAN_ARCHITECTURE_SKILLS

ALL_SKILLS = (
    WEB_FRAMEWORKS_SKILLS
    + UI_DESIGN_SKILLS
    + DATABASES_STORAGE_SKILLS
    + AI_LLM_SKILLS
    + DEVOPS_CLOUD_SKILLS
    + SECURITY_SAST_SKILLS
    + TESTING_QA_SKILLS
    + BUSINESS_ECOMMERCE_SKILLS
    + CLEAN_ARCHITECTURE_SKILLS
)

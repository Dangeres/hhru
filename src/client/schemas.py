from datetime import datetime
from enum import Enum
from typing import Dict
from pydantic import BaseModel, Field


class SearchClustersOrder(BaseModel):
    work_schedule_by_days: list[str]
    employment_form: list[str]
    work_format: list[str]
    experience: list[str]
    industry: list[str]
    area: list[str]
    professional_role: list[str]
    education: list[str]
    working_hours: list[str]
    label: list[str]
    search_field: list[str]
    excluded_text: list[str]
    resume: list[str]


class SearchCounts(BaseModel):
    isLoad: bool
    value: int
    usedResumeId: int
    isSuitableSearch: bool


class SavedSearches(BaseModel):
    isSavedSearch: bool
    email: str
    isFormOpen: bool
    isShowButton: bool
    position: int


class Criteria(BaseModel):
    page: int
    limit: int
    offset: int
    clusters: bool
    currency_code: str
    search_debug: bool
    control_flag: list[str]
    saved_search_id: None
    search_session_id: str
    vacancy_id: None
    resume: str
    no_magic: bool
    ored_clusters: bool
    cache_ttl_sec: None
    text: str
    date_from: None
    date_to: None
    items_on_page: int
    order_by: str
    search_field: list[str]
    enable_snippets: bool
    only_with_salary: bool
    is_part_time_clusters_enabled: bool
    exclude_archived: bool
    exclude_closed: bool
    search_period: None
    salary: None
    bottom_left_lat: None
    bottom_left_lng: None
    top_right_lat: None
    top_right_lng: None
    sort_point_lat: None
    sort_point_lng: None
    employer_id: None
    excluded_employer_id: None
    employer_manager_id: None
    precision: None
    geocode_type: None
    geohash: None
    recommended_by_uid: bool
    excluded_text: str
    accept_temporary: None
    use_relations_for_similar: None


class Vacancie(BaseModel):
    vacancyId: int
    name: str
    type: str
    acceptTemporary: bool
    metallic: str
    creationSite: str
    creationSiteId: int
    displayHost: str
    creationTime: datetime
    canBeShared: bool
    inboxPossibility: bool
    chatWritePossibility: str
    notify: bool
    acceptIncompleteResumes: bool
    workExperience: str
    closedForApplicants: bool
    userTestPresent: bool
    employmentForm: str
    internship: bool
    nightShifts: bool
    contactInfo: None
    responsesCount: int
    totalResponsesCount: int
    show_question_input: bool
    allowChatWithManager: bool
    searchRid: str


class ProxiedSearchFormParams(BaseModel):
    search_session_id: str
    resume: str
    ored_clusters: bool
    text: str
    enable_snippets: bool
    excluded_text: str


class SelectedCluster(BaseModel):
    name: str
    title: str


class EmployerReviews(BaseModel):
    totalRating: str
    reviewsCount: int


class Company(BaseModel):
    id: int
    name: str
    visibleName: str
    employerOrganizationFormId: int
    companySiteUrl: str
    accreditedITEmployer: bool
    employerReviews: EmployerReviews


class Compensation(BaseModel):
    to: int
    currencyCode: str
    gross: bool
    perModeFrom: int
    perModeTo: int
    mode: str


class Area(BaseModel):
    name: str
    path: str


class EmployerManager(BaseModel):
    latestActivity: str


class Links(BaseModel):
    desktop: str
    mobile: str


class Language(BaseModel):
    language: list[str]


class WorkScheduleByDay(BaseModel):
    workScheduleByDaysElement: list[str]


class WorkingHour(BaseModel):
    workingHoursElement: list[str]


class ExperimentalMode(BaseModel):
    experimentalMode: list[str]


class Snippet(BaseModel):
    req: str
    resp: str
    cond: str
    skill: str
    desc: None


class Previous(BaseModel):
    page: int
    disabled: bool


class Property(BaseModel):
    id: int
    propertyType: str
    defining: bool
    classifying: bool
    bundle: str
    propertyWeight: int
    startTimeIso: datetime
    endTimeIso: datetime


class Hh(BaseModel):
    advertising: bool
    anonymous: bool
    filteredPropertyNames: list[str]
    free: bool
    optionPremium: bool
    payForPerformance: bool
    premium: bool
    standard: bool
    standardPlus: bool
    translationKeys: list[str]
    translation: str


class VacancySearchResult(BaseModel):
    savedSearches: SavedSearches
    criteria: Criteria
    totalUsedFilters: int
    vacancies: list[Vacancie]
    hasVacanciesWithAddress: bool
    isClustersEnabled: bool
    totalResults: int
    enableSimilarSavedSearch: bool
    showSwipeTeaser: bool
    proxiedSearchFormParams: ProxiedSearchFormParams
    vacancyHint: None


class SearchResponse(BaseModel):
    searchClustersOrder: SearchClustersOrder
    searchCounts: SearchCounts
    vacancySearchResult: VacancySearchResult


class Resume(BaseModel):
    title: str = Field(description="Название резюме")
    href: str = Field(description="Токен для ссылки на резюме")
    updated: int = Field(description="Время последнего поднятия")
    bump_at: int = Field(description="Когда нужно его поднять в поиске")


class MethodEnum(Enum):
    head = "head"
    post = "post"
    get = "get"


class Tokens(BaseModel):
    xsrf: str = Field()
    hhtoken: str = Field()


class Config(BaseModel):
    username: str = Field(description="Логин авторизации")
    password: str = Field(description="Пароль авторизации")
    folder_tokens: str = Field(description="Токены сессии")
    url: str = Field(description="Урлина сайта hh")
    verify_ssl: bool = Field(description="SSL")
    proxy: Dict[str, str] | None = Field(description="Прокся для запросов")
    black_list_company: list[int] = Field(
        description="Черный список компаний, все вакансии будут скипаться"
    )
    black_words: list[str] = Field(description="Черные слова для поиска вакансий")

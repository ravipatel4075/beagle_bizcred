from enum import Enum


def human_readable(value):
    value = value.replace('__1__', '_/_')
    value = value.replace('__2__', '_-_')
    value = value.replace('__3__', ',_')
    value = value.split('_')
    value = [word[0:1].upper() + word[1:].lower() for word in value]
    value = ' '.join(value).strip()
    return value


def to_choices(e):
    e_dict = dict(e.__members__)
    return [(e_dict[k].value, human_readable(k)) for k in e_dict]


class Month(Enum):
    SELECT = ''
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


class Gender(Enum):
    SELECT = ''
    MALE = 1
    FEMALE = 2
    OTHER = 3


class MonthlyIncome(Enum):
    SELECT = ''
    BETWEEN_10K_AND_25K = 1
    BETWEEN_25K_AND_50K = 2
    BETWEEN_50K_AND_100K = 3
    ABOVE_100K = 4


class GrossTurnover(Enum):
    SELECT = ''
    BETWEEN_50_LACS_AND_1_CRORE = 1
    BETWEEN_1_CRORE_AND_2_CRORES = 2
    BETWEEN_2_CRORES_AND_5_CRORES = 3
    BETWEEN_5_CRORES_AND_10_CRORES = 4
    BETWEEN_10_CRORES_AND_50_CRORES = 5
    ABOVE_50_CRORE = 6


class HouseType(Enum):
    SELECT = ''
    OWNED_BY_YOU = 1
    OWNED_BY_PARENTS = 2
    RENTED = 3


# class EmploymentType(Enum):
#     SALARIED = 1
#     SELF_EMPLOYEED = 2
#     RETIRED = 3


class LoanReason(Enum):
    SELECT = ''
    WEDDING = 1
    MEDICAL = 2
    VEHICLE = 3
    EDUCATION = 4
    FURNITURE = 5
    ELECTRONICS = 6
    BUSINESS = 7
    OTHERS = 0


class IndiaStates(Enum):
    SELECT = ''
    ANDAMAN_AND_NICOBAR_ISLANDS = 1
    ANDHRA_PRADESH = 2
    ARUNACHAL_PRADESH = 3
    ASSAM = 4
    BIHAR = 5
    CHANDIGARH = 6
    CHHATTISGARH = 7
    DADRA_AND_NAGAR_HAVELI = 8
    DAMAN_AND_DIU = 9
    DELHI = 10
    GOA = 11
    GUJARAT = 12
    HARYANA = 13
    HIMACHAL_PRADESH = 14
    JAMMU_AND_KASHMIR = 15
    JHARKHAND = 16
    KARNATAKA = 17
    KERALA = 18
    LADAKH = 19
    LAKSHADWEEP = 20
    MADHYA_PRADESH = 21
    MAHARASHTRA = 22
    MANIPUR = 23
    MEGHALAYA = 24
    MIZORAM = 25
    NAGALAND = 26
    ORISSA = 27
    PONDICHERRY = 28
    PUNJAB = 29
    RAJASTHAN = 30
    SIKKIM = 31
    TAMIL_NADU = 32
    TELANGANA = 33
    TRIPURA = 34
    UTTAR_PRADESH = 35
    UTTARAKHAND = 36
    WEST_BENGAL = 37


IndiaStateCodes = {
    "AN":"ANDAMAN_AND_NICOBAR_ISLANDS",
    "AP":"ANDHRA_PRADESH", 
    "AR":"ARUNACHAL_PRADESH", 
    "AS":"ASSAM", 
    "BR":"BIHAR",
    "CG":"CHANDIGARH",
    "CH":"CHHATTISGARH",
    "DN":"DADRA_AND_NAGAR_HAVELI",
    "DD":"DAMAN_AND_DIU",
    "DL":"DELHI",
    "GA":"GOA",
    "GJ":"GUJARAT",
    "HR":"HARYANA",
    "HP":"HIMACHAL_PRADESH",
    "JK":"JAMMU_AND_KASHMIR",
    "JH":"JHARKHAND",
    "KA":"KARNATAKA",
    "KL":"KERALA",
    "LA":"LADAKH",
    "LD":"LAKSHADWEEP",
    "MP":"MADHYA_PRADESH",
    "MH":"MAHARASHTRA",
    "MN":"MANIPUR",
    "ML":"MEGHALAYA",
    "MZ":"MIZORAM",
    "NL":"NAGALAND",
    "OR":"ORISSA",
    "PY":"PONDICHERRY",
    "PB":"PUNJAB",
    "RJ":"RAJASTHAN",
    "SK":"SIKKIM",
    "TN":"TAMIL_NADU",
    "TS":"TELANGANA",
    "TR":"TRIPURA",
    "UP":"UTTAR_PRADESH",
    "UK":"UTTARAKHAND",
    "WB":"WEST_BENGAL"
    }

class AddressType(Enum):
    SELECT = ''
    CURRENT = 1
    PERMANENT = 2


class EducationLevel(Enum):
    SELECT = ''
    HIGH_SCHOOl = 1
    DIPLOMA = 2
    GRADUATE = 3
    POST_GRADUATE = 4
    PROFESSIONAl = 5


class MaritalStatus(Enum):
    SELECT = ''
    SINGLE = 1
    MARRIED = 2
    DIVORCED = 3
    WIDOWED = 4


class EmploymentIndustry(Enum):
    SELECT = ''
    AGRICULTURE__1__FORESTRY__1__FISHING = 1
    METALS_AND_MINERALS = 2
    ENERGY_AND_UTILITIES = 3
    CONSTRUCTION__2__INDUSTRIAL_FACILITIES_AND_INFRASTRUCTURE = 4
    AEROSPACE_AND_DEFENSE = 6
    AUTOMOTIVE_AND_PARTS_MFG = 7
    BIOTECHNOLOGY__1__PHARMACEUTICALS = 8
    CHEMICALS__1__PETRO__2__CHEMICALS = 9
    CONSUMER_PACKAGED_GOODS_MANUFACTURING = 10
    ELECTRONICS__3__COMPONENTS__3__AND_SEMICONDUCTOR_MFG = 11
    MANUFACTURING__2__OTHER = 12
    PRINTING_AND_PUBLISHING = 13
    CLOTHING_AND_TEXTILE_MANUFACTURING = 14
    WHOLESALE_TRADE__1__IMPORT__2__EXPORT = 15
    RETAIL = 17
    TRAVEL__3__TRANSPORTATION_AND_TOURISM = 18
    TRANSPORT_AND_STORAGE__2__MATERIALS = 19
    INTERNET_SERVICES = 20
    BROADCASTING__3__MUSIC__3__AND_FILM = 21
    TELECOMMUNICATIONS_SERVICES = 22
    BANKING = 23
    INSURANCE = 24
    REAL_ESTATE__1__PROPERTY_MANAGEMENT = 26
    RENTAL_SERVICES = 27
    ACCOUNTING_AND_AUDITING_SERVICES = 28
    ADVERTISING_AND_PR_SERVICES = 29
    ARCHITECTURAL_AND_DESIGN_SERVICES = 30
    MANAGEMENT_CONSULTING_SERVICES = 31
    COMPUTER_HARDWARE = 32
    COMPUTER_SOFTWARE = 33
    LEGAL_SERVICES = 34
    WASTE_MANAGEMENT = 37
    EDUCATION = 38
    HEALTHCARE_SERVICES = 39
    PERFORMING_AND_FINE_ARTS = 42
    SPORTS_AND_PHYSICAL_RECREATION = 43
    HOTELS_AND_LODGING = 44
    RESTAURANT__1__FOOD_SERVICES = 45
    STAFFING__1__EMPLOYMENT_AGENCIES = 46
    NONPROFIT_CHARITABLE_ORGANIZATIONS = 47
    PERSONAL_AND_HOUSEHOLD_SERVICES = 48
    GOVERNMENT_AND_MILITARY = 50
    SECURITY_AND_SURVEILLANCE = 74
    AUTOMOTIVE_SALES_AND_REPAIR_SERVICES = 75
    BUSINESS_SERVICES__2__OTHER = 76
    INFORMATION_TECHNOLOGY_SERVICES = 77
    CONSTRUCTION__2__RESIDENTIAL_AND_COMMERCIAL__1__OFFICE = 78
    ENGINEERING_SERVICES = 79
    ENTERTAINMENT_VENUES_AND_THEATERS = 80
    FINANCIAL_SERVICES = 81
    FOOD_AND_BEVERAGE_PRODUCTION = 82
    MARINE_MFG_AND_SERVICES = 83
    MEDICAL_DEVICES_AND_SUPPLIES = 84
    OTHERS = 85


class EmploymentDuration(Enum):
    SELECT = ''
    LESS_THAN_1_YEAR = 1
    BETWEEN_1_AND_2_YEARS = 2
    BETWEEN_3_AND_5_YEARS = 3
    BETWEEN_5_AND_7_YEARS = 4
    BETWEEN_7_AND_10_YEARS = 5
    BETWEEN_10_AND_15_YEARS = 6
    OVER_15_YEARS = 7


class AccountType(Enum):
    SELECT = ''
    INDIVIDUAL = 1
    INSTITUTION = 2
    DEALER = 4
    LENDER = 3
    


class OtpType(Enum):
    SELECT = ''
    EMAIL = 1
    TEXT = 2


class BankAccountType(Enum):
    SELECT = ''
    CURRENT = 1
    SAVINGS = 2


class VeloceRating(Enum):
    SELECT = ''
    V1 = 1
    V2 = 2
    V3 = 3
    V4 = 4
    V5 = 5


class VeloceMarginPayer(Enum):
    SELECT = ''
    LENDER = 1
    BORROWER = 2


class OrganizationType(Enum):
    SELECT = ''
    LLP = 1
    PVT_LTD = 2
    LTD = 3
    BANK = 4
    NBFC = 5
    PARTNERSHIP = 6


class EmploymentType(Enum):
    SELECT = ''
    SELF_EMPLOYED = 1
    SALARIED = 2

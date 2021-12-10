from bizcred.modules.general import GENERAL_MODULE
from bizcred.modules.phone import PHONE_MODULE
from bizcred.modules.aadhar import AADHAR_MODULE
from bizcred.modules.bank_statement import BANKSTATEMENT_MODULE
from bizcred.modules.bank import BANK_MODULE, Lender_Details_MODULE
from bizcred.modules.company_details import COMPANY_DETAILS_MODULE
from bizcred.modules.business_financial import BUSINESS_FINANCIAL_MODULE
from bizcred.modules.employment_details import EMPLOYMENT_DETAIL_MODULE
from bizcred.modules.gst import GST_MODULE, OPTIONAL_GST_MODULE
from bizcred.modules.itr import ITR_MODULE
from bizcred.modules.pan import PAN_MODULE
from bizcred.modules.identification import IDENTIFICATION_MODULE
# from bizcred.modules.financial_details import FINANCIAL_STATEMENTS_MODULE
from bizcred.modules.sanctioned_loans import SANCTIONED_LOANS_MODULE
from bizcred.modules.address import CURRENT_ADDRESS_MODULE, OFFICE_ADDRESS_MODULE
from bizcred.modules.additional_company_details import ADDITIONAL_COMPANY_DETAILS_MODULE, Auth_ADDITIONAL_COMPANY_DETAILS_MODULE
from bizcred.modules.related_company import RELATED_COMPANY_MODULE
from bizcred.enums import AccountType


FORM_MAP = {
    AccountType.INDIVIDUAL.value: [
        # Level 0
        GENERAL_MODULE,
        PHONE_MODULE,
        CURRENT_ADDRESS_MODULE,

        # Level 1
        # PAN_MODULE,
        # AADHAR_MODULE,
        # OPTIONAL_GST_MODULE,
        # Level 2
        IDENTIFICATION_MODULE,
        BANK_MODULE,
        ITR_MODULE,
        # FINANCIAL_STATEMENTS_MODULE,
        BUSINESS_FINANCIAL_MODULE,
        EMPLOYMENT_DETAIL_MODULE,
        BANKSTATEMENT_MODULE,
        SANCTIONED_LOANS_MODULE,
    ],
    AccountType.INSTITUTION.value: [
        # Level 0
        COMPANY_DETAILS_MODULE,
        GENERAL_MODULE,
        PHONE_MODULE,
        OFFICE_ADDRESS_MODULE,

        # Level 1
        # PAN_MODULE,
        # GST_MODULE,

        # Level 2
        ADDITIONAL_COMPANY_DETAILS_MODULE,
        Auth_ADDITIONAL_COMPANY_DETAILS_MODULE,
        # FINANCIAL_STATEMENTS_MODULE,
        BANK_MODULE,
        ITR_MODULE,
        BUSINESS_FINANCIAL_MODULE,
        BANKSTATEMENT_MODULE,
        SANCTIONED_LOANS_MODULE,
        RELATED_COMPANY_MODULE,
    ],
    AccountType.DEALER.value: [
        # Level 0
        COMPANY_DETAILS_MODULE,
        GENERAL_MODULE,
        PHONE_MODULE,
        OFFICE_ADDRESS_MODULE,

        # Level 1
        # PAN_MODULE,
        # GST_MODULE,

        # Level 2
        ADDITIONAL_COMPANY_DETAILS_MODULE,
        Auth_ADDITIONAL_COMPANY_DETAILS_MODULE,
        # FINANCIAL_STATEMENTS_MODULE,
        BANK_MODULE,
        ITR_MODULE,
        BUSINESS_FINANCIAL_MODULE,
        BANKSTATEMENT_MODULE,
        SANCTIONED_LOANS_MODULE,
        RELATED_COMPANY_MODULE,
    ],
    AccountType.LENDER.value: [
        # Level 0
        COMPANY_DETAILS_MODULE,
        GENERAL_MODULE,
        PHONE_MODULE,
        OFFICE_ADDRESS_MODULE,

        # Level 1
        # PAN_MODULE,
        # GST_MODULE,

        # Level 2
        ADDITIONAL_COMPANY_DETAILS_MODULE,
        Auth_ADDITIONAL_COMPANY_DETAILS_MODULE,
        # FINANCIAL_STATEMENTS_MODULE,
        Lender_Details_MODULE,
        BANK_MODULE
    ]
}

MASKS = {}  
for account_type in FORM_MAP:
    MASKS[account_type] = 0
    for i, module in enumerate(FORM_MAP[account_type]):
        if not module.level > 1:
            MASKS[account_type] |= (1 << i)


# ravi
# MASKS = {}  
# for account_type in FORM_MAP:
#     print('############ account type #######',account_type) #1,2,3
#     MASKS[account_type] = 0
#     # print('###### Masks before #########', MASKS ) # {1: 0},{1: 7, 2: 0},{1: 7, 2: 15, 3: 0}
#     print('##########form_map[account_type]',FORM_MAP[account_type])
#     # print('######## enumerate #####',enumerate(FORM_MAP[account_type]))
#     for i, module in enumerate(FORM_MAP[account_type]):
#         # print('###### Masks #########', MASKS ) # {1: 0},{1: 7, 2: 0},{1: 7, 2: 15, 3: 0}
#         # print('######## i and module ##########',i,module) # i(1) = range(0,9), i(2) = range(0,11), i(3) = range(0,7) # module get all the module from the models
#         # print(module.level) # each and every models level are written in models by level=1
#         if not module.level > 1:
#             # print('##### module.level (if) ######',module.level) #till 30 time loop run and filter 11 models define as level-1
#             MASKS[account_type] |= (1 << i)
#             # print('masks',MASKS)
#             # print('if ######',MASKS[account_type]) #7,15,15
#             # print((1 << i))
#         # else:
#             # print('##### module.level (else) ######',module.level) #till 30 time loop run filter 19 models define as level-2 and level-3
#             # print('masks',MASKS)
#             # print('else ######',MASKS[account_type]) #7,15,15
#             # print((1 << i))



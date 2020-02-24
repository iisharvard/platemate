# QUALIFICATIONS
# The magic constants for QualificationTypeId are documented in
# https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html#ApiReference_QualificationType-IDs
# --------------


def min_approval(score):
    qualification = {
        'QualificationTypeId': '000000000000000000L0',
        'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [score],
        'ActionsGuarded': 'Accept',
    }
    return qualification


def min_completed(hits):
    qualification = {
        'QualificationTypeId': '00000000000000000040',
        'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [hits],
        'ActionsGuarded': 'Accept',
    }
    return qualification


def locale(country_code):
    # http://www.iso.org/iso/country_codes/iso_3166_code_lists/english_country_names_and_code_elements.htm
    qualification = {
        'QualificationTypeId': '00000000000000000071',
        'Comparator': 'EqualTo',
        'LocaleValues':[{
            'Country': country_code
        }],
        'ActionsGuarded': 'Accept',
    }
    return qualification

from boto.mturk import qualification

# QUALIFICATIONS
# --------------
def min_approval(score):
    return qualification.PercentAssignmentsApprovedRequirement('GreaterThanOrEqualTo', score).get_as_params()

def min_completed(hits):
    return qualification.NumberHitsApprovedRequirement('GreaterThanOrEqualTo', hits).get_as_params()

def locale(country_code):
    # http://www.iso.org/iso/country_codes/iso_3166_code_lists/english_country_names_and_code_elements.htm
    return qualification.LocaleRequirement('EqualTo', country_code, True).get_as_params()

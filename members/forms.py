from django import forms
from .models import Member

# Starter list of UCC programmes. Please compare it with UCC's current
# official catalogue before treating it as a complete list.
UCC_PROGRAMMES = [
    # EDUCATION
    "B.Ed. Accounting",
    "B.Ed. Accounting with ICT",
    "B.Ed. Accounting with Management",
    "B.Ed. Accounting with Mathematics",
    "B.Ed. Agriculture",
    "B.Ed. Arabic",
    "B.Ed. Arts",
    "B.Ed. Automobile and Metal Technology",
    "B.Ed. Basic Education",
    "B.Ed. Building and Wood Technology",
    "B.Ed. Clothing and Textiles with Management in Living",
    "B.Ed. Communication Design",
    "B.Ed. Early Childhood Education",
    "B.Ed. English",
    "B.Ed. French",
    "B.Ed. Geography",
    "B.Ed. History",
    "B.Ed. Home Economics",
    "B.Ed. Information Technology",
    "B.Ed. Junior High School Education",
    "B.Ed. Mathematics",
    "B.Ed. Physical Education",
    "B.Ed. Primary Education",
    "B.Ed. Science",
    "B.Ed. Social Science",
    "B.Ed. Social Studies",
    "B.Ed. Special Education",
    "B.Ed. Technical/Vocational Education",
    "B.Ed. Visual Arts",

    # ARTS, HUMANITIES AND SOCIAL SCIENCES
    "B.Sc. Psychology",
    "B.A. African Studies",
    "B.A. Anthropology",
    "B.A. Arts",
    "B.A. Chinese",
    "B.A. Communication Studies",
    "B.A. Dance",
    "B.A. Film Studies",
    "B.A. Information Science",
    "B.A. Linguistics",
    "B.A. Population and Health",
    "B.A. Social Sciences",
    "B.A. Theatre and Drama",
    "B.A. Theatre Studies",
    "B.Mus. Music",
    "B.Mus. General Studies",
    "LL.B. Law",

    # BUSINESS AND COMMERCE
    "B.Com. Accounting",
    "B.Com. Entrepreneurship and Graphic Design",
    "B.Com. Entrepreneurship with Graphic Design",
    "B.Com. Entrepreneurship with International Business",
    "B.Com. Finance",
    "B.Com. Human Resource Management",
    "B.Com. Management",
    "B.Com. Marketing",
    "B.Com. Procurement and Supply Chain Management",

    # AGRICULTURE, SCIENCE, ENGINEERING AND TECHNOLOGY
    "B.Sc. Accounting and Finance",
    "B.Sc. Actuarial Science",
    "B.Sc. Agribusiness",
    "B.Sc. Agricultural Extension and Community Development",
    "B.Sc. Agriculture",
    "B.Sc. Agro-Processing",
    "B.Sc. Animal Production (Post-Diploma)",
    "B.Sc. Applied Economics",
    "B.Sc. Biochemistry",
    "B.Sc. Biomedical Sciences",
    "B.Sc. Chemical Engineering",
    "B.Sc. Chemistry",
    "B.Sc. Computer Engineering",
    "B.Sc. Computer Science",
    "B.Sc. Conservation Biology and Entomology",
    "B.Sc. Data Science and Economic Policy",
    "B.Sc. Diagnostic Imaging Technology",
    "B.Sc. Diagnostic Medical Sonography",
    "B.Sc. Economics",
    "B.Sc. Economics with Finance",
    "B.Sc. Engineering Physics",
    "B.Sc. Environmental Science",
    "B.Sc. Fisheries and Aquatic Sciences",
    "B.Sc. Forensic Science",
    "B.Sc. Geography and Regional Planning",
    "B.Sc. Health Information Management",
    "B.Sc. Horticulture",
    "B.Sc. Industrial Chemistry",
    "B.Sc. Information Technology",
    "B.Sc. Laboratory Technology",
    "B.Sc. Mathematics",
    "B.Sc. Mathematics and Statistics",
    "B.Sc. Mathematics with Business",
    "B.Sc. Mathematics with Economics",
    "B.Sc. Meteorology and Atmospheric Physics",
    "B.Sc. Molecular Biology and Biotechnology",
    "B.Sc. Nursing",
    "B.Sc. Physics",
    "B.Sc. Statistics",
    "B.Sc. Tourism Management",
    "B.Sc. Water and Sanitation",
    "B.Sc. Hospitality Management",
    "B.Sc. Marketing",
    "B.Sc. Sports and Exercise Science",
    "B.Sc. Clinical Nutrition and Dietetics",
    "B.Sc. Medical Laboratory Technology",
    "B.Sc. Physician Assistant Studies",
    "B.Sc. Mental Health Nursing",
    "B.Sc. Community Mental Health Nursing",
    "B.Sc. Midwifery",
    "B.Sc. Midwifery (Post-Diploma)",
    "B.Sc. Health, Physical Education and Recreation",
    "B.Sc. Entomology and Wildlife",
    "B.Sc. Agricultural Extension (Post-Diploma)",
    "B.Sc. Psychology",
    "B.Sc. Soil Science",
    "B.Sc. Animal Science",
    "B.Sc. Crop Science",
    "B.Sc. Food Science and Technology",
    "B.Sc. Environmental Management",
    "B.Sc. Marine and Fisheries Sciences",
    "B.Sc. Public Health",
    "B.Sc. Human Resource Management",
    "B.Sc. Management",
    "B.Sc. Finance",
    "B.Sc. Procurement and Supply Chain Management",
    "B.Sc. Communication Design",
    "B.Sc. Mathematics and ICT Education",
    "B.Sc. Science Education",
    "B.Sc. Computer Science Education",
    "B.Sc. Integrated Development Studies",
    "B.Sc. Peace Studies",
    "B.Sc. Sociology and Anthropology",
    "B.Sc. Religion and Human Values",
    "B.Sc. English",
    "B.Sc. French",
    "B.Sc. Ghanaian Languages",
    "B.Sc. Music and Dance",
    "B.Sc. Theatre and Film Studies",
    "B.Sc. Vision Science",

    # PROFESSIONAL DEGREES
    "Doctor of Optometry",
    "Doctor of Pharmacy",
    "Bachelor of Medicine and Bachelor of Surgery (MB ChB)",

    # DIPLOMA PROGRAMMES
    "Diploma in Accounting",
    "Diploma in Management",
    "Diploma in Information Technology in Education",
    "Diploma in Labour Studies",
    "Diploma in Social Behaviour and Conflict Management",
    "Diploma in Transport and Road Safety Management",

    # CERTIFICATE PROGRAMMES
    "Certificate in General Studies",
    "Certificate in Media Production",
    "Certificate in Labour Studies",
    "Certificate in Information Science",
    "Certificate in Herbal Medicine",
    "Certificate in Cultural and Creative Arts Management",
    "Certificate in Conflict Management and Human Development",
    "Certificate in Professional Microfinance",
    "Certificate in Montessori Education",
    "Certificate in Disability Studies",
    "Certificate in Basic Education",
    "Certificate in Early Childhood Education",
    "Certificate in Microfinance",
]

class MemberForm(forms.ModelForm):
    course = forms.ChoiceField(
        choices=[("", "Select Course")] + [
            (programme, programme)
            for programme in UCC_PROGRAMMES
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Member
        fields = [
            "full_name",
            "date_of_birth",
            "phone_number",
            "course",
            'level',
            "residential_area",
            "zone",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Enter full name"
            }),
            "date_of_birth": forms.DateInput(attrs={
                "type": "date"
            }),
            "phone_number": forms.TextInput(attrs={
                "placeholder": "Enter phone number"
            }),
            "residential_area": forms.TextInput(attrs={
                "placeholder": "Enter residential area"
            }),
        }

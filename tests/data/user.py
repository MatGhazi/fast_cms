
test_admin = {
    'username': 'test_admin',
    'mobile': '+989399093061',
    'email': 'admin.lopeun@gmail.com',
    'password': 'Aa_@$_123',
}


test_user = {
    'username': 'test_farhaad',
    'mobile': '+989219129545',
    'email': 'farhaad.lopeun@gmail.com',
    'password': 'Aa_123_@$',
}


username_data = [
    ({'username':'a'}, 422, False),
    ({'username':'123456789'}, 422, False),
    ({'username':'!@#$%^&'}, 422, False),
    ({'username':'abc!'}, 422, False),
    ({'username':'abc def'}, 422, False),
    ({'username':'abc.def'}, 422, False),
    ({'username':'qwerty'}, 200, True),
    ({'username':'qwerty_876'}, 200, True),
]


join_data = [
    ({
        'username': '',
        'mobile': '+989219129545',
        'email': 'farhaad.lopeun@gmail.com',
        'password': 'Aa_123_@$',
    }, 422, False),
    ({
        'username': 'test_farhaad',
        'mobile': '+9892191295454321',
        'email': 'farhaad.lopeun@gmail.com',
        'password': 'Aa_123_@$',
    }, 422, False),
    ({
        'username': 'test_farhaad',
        'mobile': '+989219129',
        'email': 'farhaad.lopeun@gmail.com',
        'password': 'Aa_123_@$',
    }, 422, False),
    ({
        'username': 'test_farhaad',
        'mobile': '+989219129545',
        'email': 'farhaad.lopeun.gmail.com',
        'password': 'Aa_123_@$',
    }, 422, False),
    ({
        'username': 'test_farhaad',
        'mobile': '+989219129545',
        'email': 'farhaad.lopeun@gmail',
        'password': 'Aa_123_@$',
    }, 422, False),
    ({
        'username': 'test_farhaad',
        'mobile': '+989219129545',
        'email': 'farhaad.lopeun@gmail.com',
        'password': 'Aa123',
    }, 422, False),
    (test_user, 200, True),
    (test_user, 422, False),
]


login_data = [
    ({'usemo': 'farhaad', 'password': 'Aa_123_@$'}, 401, False),
    ({'usemo': 'test_farhaad', 'password': 'Aa__@$'}, 401, False),
    ({'usemo': 'test_farhaad', 'password': 'Aa_123_@$'}, 200, True),
    ({'usemo': '+989219129545', 'password': 'Aa_123_@$'}, 200, True),
    ({'usemo': 'farhaad.lopeun@gmail.com', 'password': 'Aa_123_@$'}, 200, True),
]


profile_data = [
    ({'first_name': '', 'last_name': '', 'bio': ''}, 200, True),
    ({'first_name': 'John', 'last_name': 'Doe', 'bio': '...'}, 200, True),
]


otp_request_data = [
    ({'usemo': 'test_far'}, 406, False),
    ({'usemo': 'test_farhaad'}, 200, True),
    ({'usemo': '+989219129545'}, 406, False),
    ({'usemo': 'farhaad.lopeun@gmail.com'}, 406, False),
]


reset_password_data = [
    ({'usemo': 'test_far', 'password': 'Zz_123_@$'}, 406, False),
    ({'usemo': 'test_farhaad', 'password': '123'}, 422, False),
    ({'usemo': 'test_farhaad', 'password': 'Zz_123_@$'}, 200, True),
]


deleteme_data = [
    ({'reason': ''}, 422, False),
    ({'reason': 'abc'}, 422, False),
    ({'reason': 'Wanna check what would happen'}, 200, True),
    ({'reason': 'Just for fun'}, 200, True),
    ({'reason': 'Nothing'}, 200, True),
    ({'reason': '+ Just a test'}, 200, True),
]


user_pagination_data = [
    {},
    {'page':2},
    {'page':2, 'page_size':1},
    {'page':1, 'page_size':5},
    {'page':1, 'desc':True},
    {'page':1, 'desc':True, 'sort':'username'},
]


image_pagination_data = [
    {},
    {'page':2},
    {'page':2, 'page_size':1},
    {'page':2, 'page_size':5},
    {'page':1, 'desc':True},
    {'page':1, 'desc':True, 'sort':'model'},
    {'page':1, 'desc':True, 'model':'User'},
    {'page':1, 'desc':True, 'model':'User', 'field':'avatar'},
    {'page':1, 'desc':True, 'field':'avatar'},
]


from jwt import decode

from backend.security import SECRET_KEY, SECURITY_TYPE, create_access_token


def test_encode_token():
    data = {'sub': 'vini@vini.com'}
    token = create_access_token(data)
    result = decode(token, SECRET_KEY, [SECURITY_TYPE])
    assert result['sub'] == data['sub']
    assert result['exp']

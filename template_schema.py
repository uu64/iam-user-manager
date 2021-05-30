
#!/usr/bin/env python3

schema = {
    'Users': {
        'type': 'list',
        'required': True,
        'schema': {
            'type': 'dict',
            'required': True,
            'schema': {
                'Name': {
                    'type': 'string',
                    'required': True
                },
                'Tags': {
                    'type': 'dict',
                    'required': False,
                    'keysrules': {
                        'type': 'string'
                    },
                    'valuesrules': {
                        'type': 'string'
                    }
                },
                'Groups': {
                    'type': 'list',
                    'required': False,
                    'schema': {
                        'type': 'string',
                        'required': True
                    }
                }
            }
        }
    }
}
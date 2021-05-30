
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
                    'type': 'list',
                    'required': False,
                    'schema': {
                        'type': 'dict',
                        'required': True,
                        'schema': {
                            'Key': {
                                'type': 'string',
                                'required': True
                            },
                            'Value': {
                                'type': 'string',
                                'required': True
                            }
                        }
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
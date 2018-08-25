# -*- coding: utf-8 -*-
# @Date    : 2018-08-21 17:48:31
# @Author  : Md Nazrul Islam <email2nazrul@gmail.com>
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'

date_pattern = '-?[0-9]{4}(-(0[1-9]|1[0-2])(-(0[0-9]|[1-2][0-9]|3[0-1]))?)?'  # noqa: E501
datetime_pattern = '-?[0-9]{4}(-(0[1-9]|1[0-2])(-(0[0-9]|[1-2][0-9]|3[0-1])(T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]+)?(Z|(\\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00)))?)?)?'  # noqa: E501
Bool = {
    'type': 'boolean',
    'store': False,
}
Float = {
    'type': 'float',
    'store': False,
}

Integer = {
    'type': 'integer',
    'store': False,
}
Long = {
    'type': 'long',
    'store': False,
}

Token = {
    'type': 'string',
    'index': 'not_analyzed',
    'store': False,
}

Text = {
    'type': 'string',
    'index': 'analyzed',
    'store': False,
}

SearchableText = {
    'type': 'string',
    'index': 'analyzed',
    'analyzer': 'keyword',
    'store': False,
}

Date = {
    'type': 'date',
    'format': 'date_time_no_millis||date_optional_time',
    'store': False,
}

Timing = {
    'properties': {
        'event': Date,
        'code': Token,
    },
}

Reference = {
    'properties': {
        'reference': Token,
    },
}

Attachment = {
    'properties': {
        'url': Token,
        'language': Token,
        'title': Text,
        'creation': Date,
    },
}

Coding = {
    'properties': {
        'system': Token,
        'code': Token,
        'display': Token,
    },
}

CodeableConcept = {
    'properties': {
        'text': Text,
        'coding': {
            'type': 'nested',
            'properties': Coding['properties'],
        },
    },
}

Period = {
    'properties': {
        'start': Date,
        'end': Date,
    },
}
Identifier = {
    'properties': {
        'use': Token,
        'system': Token,
        'value': Token,
        'type': {
            'properties': {
                'text': Text,
            },
        },
    },
}
Quantity = {
    'properties': {
        'value': Float,
        'code': Token,
        'system': Token,
        'unit': Token,
    },
}

Money = Quantity
Range = {
    'properties': {
        'high': Quantity,
        'low': Quantity,
    },
}

Address = {
    'properties': {
        'city': Token,
        'country': Token,
        'postalCode': Token,
        'state': Token,
        'use': Token,
    },
}

HumanName = {
    'properties': {
        'family': Token,
        'text': Text,
        'prefix': Token,
        'period': Period,
        'use': Token,
    },
}
Duration = Quantity

ContactPoint = {
    'properties': {
        'period': Period,
        'rank': Integer,
        'system': Token,
        'use': Token,
        'value': Text,
    },
}

ContactDetail = {
    'properties': {
        'name': Token,
        'telecom': ContactPoint,
    },
}

ContactDetail['properties']['telecom'].update({
    'type': 'nested',
})

Annotation = {
    'properties': {
        'authorReference': Reference,
        'authorString': Text,
        'text': Text,
        'time': Date,
    },
}

Dosage = {
    'properties': {
        'asNeededBoolean': Bool,
        'asNeededCodeableConcept': CodeableConcept,
        'doseQuantity': Quantity,
        'doseRange': Range,
        'site': CodeableConcept,
        'text': Text,
        'timing': Timing,
    },
}

RelatedArtifact = {
    'properties': {
        'type': Token,
        'url': Token,
        'resource': Reference,
    },
}

Signature = {
    'properties': {
        'contentType': Token,
        'when': Date,
        'whoReference': Reference,
        'whoUri': Token,
    },
}
# Common
Id = Token
Meta = {
    'properties': {
        'versionId': Token,
        'lastUpdated': Date,
        'profile': Token,
    },
}

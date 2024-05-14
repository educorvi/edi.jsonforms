

required_categories = [
        SimpleTerm('optional', 'optional', _('Optional')),
        SimpleTerm('required', 'required', _('Required')),
        SimpleTerm('depend_required', 'depend_required', _('Dependent Required')),
        ]
Required_categories = SimpleVocabulary(required_categories)

from django import forms
from bizcred import widgets


class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        kwargs.setdefault('label_suffix', '')
        super(BaseForm, self).__init__(*args, **kwargs)


class BaseModelForm(forms.ModelForm):
    force_save = False
    skip_render = False

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.step = kwargs.get('step', 0)
        if 'step' in kwargs:
            del kwargs['step']

        kwargs.setdefault('label_suffix', '')
        super(BaseModelForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            f = self.fields[field]

            if isinstance(f, forms.DateField):
                f.widget = widgets.CustomDate(list(range(1940, 2021)))
            elif isinstance(f, forms.FileField):
                f.widget = widgets.CustomFileInput()
            elif isinstance(f, forms.BooleanField):
                f.widget = widgets.CustomCheckbox(f.label)
            elif isinstance(f, forms.ChoiceField) and len(f.choices) and f.choices[0][0] == '':
                f.choices = [('', 'Select')] + f.choices[1:]


class SkipStep(Exception):
    def __init__(self):
        pass

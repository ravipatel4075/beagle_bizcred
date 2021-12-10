from django import forms
from django.utils.safestring import mark_safe
from datetime import date

MONTHS = [
    (i, date(2020, i, 1).strftime('%B')) for i in range(1, 13)
]


class CustomCheckbox(forms.widgets.CheckboxInput):

    def __init__(self, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label

    def render(self, name, attrs=None, **kwargs):
        attrs = ' '.join([f'{k}="{attrs[k]}"' for k in attrs])
        attrs += ' '.join([f'{k}="{self.attrs[k]}"' for k in self.attrs])

        return mark_safe(f"""
        <label class="checkbox-container">
            {self.label}
            <input type="checkbox" name="{name}" {attrs}>
            <span class="checkmark"></span>
        </label>
        """)


class CustomDate(forms.widgets.DateInput):

    def __init__(self, years, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.years = years

    def render(self, name, attrs=None, **kwargs):
        attrs = ' '.join([f'{k}="{attrs[k]}"' for k in attrs])
        if 'value' in kwargs:
            attrs += ' ' + f"value=\"{kwargs['value']}\""
        attrs += ' '.join([f'{k}="{self.attrs[k]}"' for k in self.attrs])
        return mark_safe(f"""<input type="date" name="{name}" {attrs}>""")


class CustomFileInput(forms.widgets.FileInput):

    def render(self, name, value, attrs=None, **kwargs):
        filename = value.name.split('/')[-1] if value else None
        attrs['required'] = True if filename is None and attrs.get(
            'required', False) else False
        if not attrs['required']:
            del attrs['required']
        # attrs['multiple'] = True
        attrs = ' '.join([f'{k}="{attrs[k]}"' for k in attrs])
        attrs += ' '.join([f'{k}="{self.attrs[k]}"' for k in self.attrs])
        if filename is None:
            current = ''
        else:
            block = ''
            if filename.split('.')[-1] == 'jpg' or filename.split('.')[-1] == 'jpeg' or filename.split('.')[-1] == 'png' or filename.split('.')[-1] == 'gif':
                block = f'<img class="imageThumb preview-img" src="/download?path={value}" title={filename}>'
            elif filename.split('.')[-1] == 'pdf':
                block = f'<a href="/download?path={value}" target="_blank"><i class="fa fa-file-pdf-o" aria-hidden="true" style="font-size:45px;" title={filename}></i></a>'
            elif filename.split('.')[-1] == 'doc' or filename.split('.')[-1] == 'docx' or filename.split('.')[-1] == 'odt':
                print('Value************* ',value)
                block = f'<a href="/download?path={value}" download><i class="fa fa-file-word-o" aria-hidden="true" style="font-size:45px;" title={filename}></i></a>'
            elif filename.split('.')[-1] == 'csv':
                block = f'<a href="/download?path={value}" download><i class="fa fa-file-csv" aria-hidden="true" style="font-size:45px;" title={filename}></i></a>'
            elif filename.split('.')[-1] == 'xlsx' or filename.split('.')[-1] == 'xls' or filename.split('.')[-1] == 'ods':
                block = f'<a href="/download?path={value}" download><i class="fa fa-file-excel-o" aria-hidden="true" style="font-size:45px;" title={filename}></i></a>'
            if block:
                current = f""" <div class="img-wrap">
                        {block}
                        <span class="main_img_rm">X</span>
                    </div>
                """
            else:
                current = ''
        # if filename is None:
        #     current = ''
        # else:
        #     current = f"""
        #         <div class="img-wrap">
        #             <img class="imageThumb preview-img" src="/download?path={value}" title={filename}>
        #             <span class="main_img_rm">X</span>
        #         </div>
        #     """

        return mark_safe(f"""
                <div style="display:flex">
                    <input type="file" name="{name}" id="id_{name}" {attrs}>
                    </input>
                </div>
                { current if value is not None else '' }
        """)

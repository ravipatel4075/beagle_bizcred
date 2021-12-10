class Module:

    def __init__(self, title, forms, model, level=1, filterby=None, smalltitle=None):
        self.title = title
        self.forms = forms
        self.model = model
        self.level = level
        self.filter = filterby if filterby else {}
        self.smalltitle = smalltitle if smalltitle else title

    def instance(self, user, index=0):
        items = self.model.objects.filter(user__id=user.id, **self.filter)
        if len(items) <= index:
            return None, None
        else:
            instance = items[index]
            return instance, dict(instance.__dict__)

    def instances(self, user):
        return self.model.objects.filter(user__id=user.id, **self.filter)

    def get_form(self, substep=1):
        return self.forms[substep - 1]

    def get_step_form(self, step):
        return self.forms[step]

    @property
    def steps(self):
        return len(self.forms)


class ListModule(Module):

    def __init__(self, min_items, max_items=3, instance_title='Item', **kwargs):
        super().__init__(**kwargs)
        self.instance_title = instance_title
        self.min_items = min_items
        self.max_items = max_items

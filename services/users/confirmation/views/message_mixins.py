from django.shortcuts import redirect


class ValidationMessageViewMixin:
    """
    Общий класс-миксин, описывающий создание и отправку сообщения
    валидации непосредственно в представлении
    """
    message_class = None

    def form_valid(self, form):
        """
        Переопределённый метод form_valid с отправкой сообщения валидации.
        Метод переопределён без super, так как self.object обязателен для валидации,
        и должен быть раньше, чем вызов super метода, в котором может (а может и нет) быть определено
        сохранение
        """
        self.set_user_object(form)
        self.get_message(self.object).asend()
        return redirect(self.get_success_url())

    def get_message_class(self):
        """
        Метод получения класса сообщения
        """
        return self.message_class

    def get_message(self, user):
        """
        Метод получения сообщения
        """
        return self.get_message_class()(user)

    def set_user_object(self, form):
        """
        Метод, использующийся как эндпоинт между формой и представлением.
        В этом методе необходимо описать то, каким именно образом
        из формы получить объект. Объект необходимо записать в
        self.object. Так или иначе рекомендуется сохранить объект с помощью метода save
        """
        raise NotImplementedError

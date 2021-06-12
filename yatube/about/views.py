from django.views.generic import TemplateView


class AboutAuthorView(TemplateView):

    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['about_author'] = 'Очень простая страница'
        context['about_text'] = (
            'На создание этой страницы у меня ушло пять минут!'
            'Ай да я.'
        )
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def tech_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tech_title'] = 'bla bla bla'
        context['tech_text'] = 'bla bla bla text '
        return context

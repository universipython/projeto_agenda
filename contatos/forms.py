from django import forms
from .models import Contato, Grupo, Telefone, Email

class EditarContatoForm(forms.Form):
    # O método __init__() pode receber um número arbitrário de positional
    # arguments (*args) e keyword arguments (*kwargs)
    def __init__(self, *args, **kwargs):
        # Utilizamos o dicionário kwargs, formado pelos keyword arguments
        # recebidos por __init__() para fornecer o valor do id do contato
        # que estará sendo editado. O par key-value que contém a chave 'id'
        # e o valor correspondente ao id do contato são removidos do dicionário
        # kwargs através do método pop.
        # Armazenamos o objeto representando o contato em uma variável 'contato'
        contato = Contato.objects.get(id=kwargs.pop('id'))

        # Criamos um novo atributo na classe que armazena o objeto representando
        # o contato que será utilizado para criar o formulário
        self.contato = contato

        # Chamamos o método __init__() da classe mãe (Form), para que
        # EditarContatoForm tenha os mesmos atributos e comportamento desta.
        # Passamos como argumentos para este método os positional arguments
        # e keyword arguments recebidos pelo __init__()  de EditarContatoForm.
        # Lembrando que o par 'id:contato_id' foi removido do dicionário kwargs
        super(EditarContatoForm, self).__init__(*args, **kwargs)

        # Adicionamos um novo campo no formulário, 'nome_contato' que será
        # inicializado com o nome atual do contato.
        self.fields['nome_contato'] = forms.CharField(max_length=50, initial=contato.nome)

        # Recuperamos todos os grupos já armazenados no banco de dados da
        # aplicação
        grupos = Grupo.objects.all()

        # Recuperamos todos os grupos associados com o contato atual. Isso será
        # necessário para calcular os valores iniciais dos campos que
        # representam os grupos que devem estar associados com o contato.
        # Se aplicação possui 3 grupos, por exemplo, vamos mostrar três caixas
        # de seleção. E se o contato está associado com o grupo 2, por exemplo,
        # mostraremos apenas a caixa de seleção correspondente ao grupo 2
        # inicialmente selecionada.
        grupos_contato = contato.grupos.all()

        # Criamos um campo (que será uma caixa de seleção) para grupo cadastrado
        # no banco de dados da aplicação. O valor inicial de uma caixa de
        # seleção dependerá do grupo sendo iterado pertencer ou não aos grupos
        # já associados com o contato, armazenados em 'grupos_contato'
        for grupo in grupos:
            self.fields[f"g_{grupo.nome}"] = forms.BooleanField(required=False,
                                                                initial=grupo in grupos_contato,
                                                                label=f"{grupo.nome}")

        # Aqui nós criamos um campo do tipo CharField (para entrada de texto)
        # para cada telefone que estiver associado com o contato. O nome do
        # campo será 'tel_x', onde x corresponde à posição do telefone na
        # sequência de telefones retornada por 'contato.telefone_set.all()'
        for i, tel in enumerate(contato.telefone_set.all()):
            self.fields[f"tel_{i}"] = forms.CharField(max_length=14,
                                                      label=f"Telefone {i+1}",
                                                      initial=contato.telefone_set.all()[i].numero)

        # Aqui nós criamos um campo do tipo EmailField (para entrada de e-mails)
        # para cada email que estiver associado com o contato. O nome do
        # campo será 'email_x', onde x corresponde à posição do email na
        # sequência de email retornada por 'contato.email_set.all()'
        for i, email in enumerate(contato.email_set.all()):
            self.fields[f"email_{i}"] = forms.EmailField(max_length=255,
                                                         label=f"Email {i+1}",
                                                         initial=contato.email_set.all()[i].endereco)

    # Aqui nós criamos uma função que será executada automaticamente quando
    # um formulário for preenchido e enviado pelo usuário. O objetivo desta
    # função é garantir que o usuário não altere o nome do contato para um
    # nome já utilizado, a menos que seja o nome do próprio contato atual.
    def clean_nome_contato(self):
        # Armazenamos o valor de nome fornecido pelo usuário em 'nome_contato'
        nome_contato = self.cleaned_data.get('nome_contato')

        # Armazenamos os nomes de todos os contatos em uma lista 'nomes_contatos'
        nomes_contatos = []
        for contato in Contato.objects.all():
            nomes_contatos.append(contato.nome)

        # Removemos o nome do contato atual da lista de nomes de contatos
        nomes_contatos.remove(self.contato.nome)

        # Se o nome fornecido já estiver na lista 'nomes_contatos' mostraremos
        # uma mensagem de erro informando que o nome já está sendo utilizado.
        # Se não, retornamos o próprio nome fornecido pelo usuário.
        if nome_contato in nomes_contatos:
            raise forms.ValidationError("O nome escolhido já está sendo utilizado.")
        return nome_contato

class NovoGrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ('nome', 'descricao')

class NovoTelForm(forms.ModelForm):
    class Meta:
        model = Telefone
        fields = ('numero',)

class NovoEmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ('endereco',)

class EditarGrupoForm(forms.Form):
    nome = forms.CharField(max_length=50)
    descricao = forms.CharField(max_length=280, required=False)

    # criamos um novo método __init__() que será executado sempre que um
    # formulário for gerado. Este método poderá receber um número arbitrário
    # de positional arguments e keyword arguments.
    def __init__(self, *args, **kwargs):
        # Criamos um novo atributo, grupo, que armazena o objeto do tipo Grupo
        # que está associado com o formulário. Nós puxamos esse objeto do banco
        # de dados através do seu id. O id é recebido pelo formulário através
        # da view que cria este formulário. O id é enviado pela view através de
        # um keyword argument. Por isso nós pegamos o valor de 'id' do dicionário
        # kwargs.
        self.grupo = Grupo.objects.get(id=kwargs.pop('id'))

        # Agora nós chamamos o método __init__() da classe mãe, isto é, da
        # classe Form. Passamos para o método os positional arguments e keyword
        # arguments recebidos recebidos pelo formulário. Lembrando que o
        # argumento associado com a chave 'id' é removido no comando anterior.
        super(EditarGrupoForm, self).__init__(*args, **kwargs)

    # Este método valida o valor recebido pelo formulário associado com o campo
    # 'nome'
    def clean_nome(self):
        # Primeiro, nós armazenamos o valor preenchido pelo usuário na variável
        # 'nome'.
        nome = self.cleaned_data.get('nome')
        # Criamos uma lista, que inicia vazia, e logo vai armazenar os nomes
        # de todos os grupos da aplicação, exceto o nome do grupo que está
        # associado com o formulário através do atributo self.grupo, ou seja,
        # removemos o nome do grupo que está sendo editado no momento para que
        # seja possível que um grupo possa manter o seu nome após a edição.
        nomes_grupos = []
        # Utilizamos um loop para preencher a lista 'nomes_grupos' com os nomes
        # de todos os grupos da aplicação.
        for grupo in Grupo.objects.all():
            nomes_grupos.append(grupo.nome)
        # Removemos o nome do grupo que está sendo editado da lista 'nomes_grupos'
        nomes_grupos.remove(self.grupo.nome)

        # Se o nome enviado pelo usuário ao campo 'nome' estiver na lista 'nomes_grupos'
        # nós mostramos uma mensagem de erro informando que o nome já está sendo
        # utilizado
        if nome in nomes_grupos:
            raise forms.ValidationError("O nome escolhido já está sendo utilizado.")
        # Caso contrário nós apenas retornamos o nome enviado pelo usuário, pois
        # este é válido.
        else:
            return nome

class NovoContatoForm(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ('nome', 'avatar')

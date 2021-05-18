from django.shortcuts import render, get_object_or_404, redirect
from .models import Contato, Grupo, Telefone, Email
from .forms import EditarContatoForm, NovoGrupoForm, NovoTelForm, NovoEmailForm, EditarGrupoForm, NovoContatoForm

def contatos_list_view(request, grupo_id=None):
    grupo = None
    busca = None
    if grupo_id:
        grupo = get_object_or_404(Grupo, id=grupo_id)
        contatos = grupo.contato_set.all()
    elif request.POST.get('busca'):
        busca = request.POST.get('busca')
        contatos = Contato.objects.filter(nome__contains=busca)
    else:
        contatos = Contato.objects.all()
    return render(request, 'contatos/contatos_list.html', {'contatos':contatos, 'grupo':grupo, 'busca':busca})

# A view deve receber o id de um contato como argumento.
def editar_contato(request, contato_id):
    # Utilizamos o id recebido como argumento para recuperar o contato do banco
    # de dados da aplição através da função 'get_object_or_404()'.
    contato = get_object_or_404(Contato, id=contato_id)

    # Testamos se o método da requisição é o POST. Será assim quando o usuário
    # da aplicação preencher o formulário e clicar em enviar.
    if request.method == 'POST':

        # Criamos uma instância do formulário 'EditarContatoForm', fornecendo
        # o id de contato recebido pela view como keyword argument.
        form = EditarContatoForm(request.POST, id=contato_id)

        # Testamos se o form foi corretamente preenchido
        if form.is_valid():

            # Armazenamos os dados enviados pelo formulário na variável 'cd'.
            # 'cd' será um dicionário onde cada par é formado pela key
            # ao nome do campo correspondente, e o valor é o valor preenchido
            # pelo usuário no formulário.
            cd = form.cleaned_data

            # Atualizamos o nome do contato com o valor recebido pelo campo
            # 'nome_contato' do formulário
            contato.nome = cd['nome_contato']
            contato.save()

            # Criamos três listas vazias, cada uma será responsável por
            # armazenar valores fornecidos pelo usuário através do formulário.

            # 'cd_grupos' vai armazenar todos os grupos cujas caixas de seleção
            # foram selecionadas pelo usuário ao preencher o formulário.
            cd_grupos = []

            # 'cd_tels' vai armazenar os números de telefone fornecidos pelo
            # usuário através do formulário.
            cd_tels = []

            # 'cd_emails' vai armazenar os endereços de email fornecidos pelo
            # usuário através do formulário.
            cd_emails = []

            # Fazemos um loop com todos os pares key-value do dicionário cd.
            for nome, valor in cd.items():
                # Se a key do par sendo iterado começar com 'tel_', adicionamos
                # o valor associado com essa key à lista 'cd_tels'
                if nome.startswith('tel_'):
                    cd_tels.append(valor)
                # Se a key do par sendo iterado começar com 'email_', adicionamos
                # o valor associado com essa key à lista 'cd_emails'
                elif nome.startswith('email_'):
                    cd_emails.append(valor)
                # Se a key associada com o par sendo iterado começar com 'g_',
                # nós testamos se o valor associado com essa key é True.
                # Será True se a caixa de selação desse grupo estiver
                # selecionada quando o usuário enviar o formulário.
                elif nome.startswith('g_'):
                    if valor:
                        # Recuperamos, do banco de dados da aplicação,  o objeto
                        # que representa o grupo, e associamos a variável
                        # 'grupo' com esse objeto.
                        grupo =  Grupo.objects.get(nome=nome.replace('g_', ''))
                        # Por último, acrescentamos esse objeto à lista 'cd_grupos'
                        cd_grupos.append(grupo)

            # Criamos uma variável que armazena todos os telefones associados
            # com o contato.
            contato_tels = contato.telefone_set.all()

            # Criamos uma variável que armazena todos os emails associados
            # com o contato.
            contato_emails = contato.email_set.all()

            # Criamos uma variável que armazena todos os grupos associados
            # com o contato.
            contato_grupos = contato.grupos.all()

            # Fazemos um loop com a lista 'contato_tels', que armazena os
            # telefones associados com o contato. Então, atualizamos o atributo
            # 'numero', de cada telefone, com um número da lista 'cd_tels', que
            # contém os números de telefone fornecidos pelo usuário através
            # do formulário
            for i, tel in enumerate(contato_tels):
                tel.numero = cd_tels[i]
                tel.save()

            # Fazemos um loop com a lista 'contato_emails', que armazena os
            # emails associados com o contato. Então, atualizamos o atributo
            # 'endereço', de cada email, com o endereço de email da lista
            # 'cd_emails', que contém os endereços fornecidos pelo usuário
            # através do formulário.
            for i, email in enumerate(contato_emails):
                email.endereco = cd_emails[i]
                email.save()

            # Fazemos um loop com a lista 'contato_grupos', que armazena todos
            # os grupos que estão inicialmente associados com o contato.
            # O objetivo deste loop é remover o que não deveria estar lá.
            for grupo in contato_grupos:
                # Se o grupo sendo iterado é um elemento da lista 'cd_grupos',
                # que armazena os grupos cujas caixas de seleção foram selecionadas
                # no formulário, não fazemos nada.
                if grupo in cd_grupos:
                    pass
                # Mas, se o grupo sendo iterado não fizer parte da lista
                # 'cd_grupos', removemos a associação desse grupo com o contato.
                else:
                    contato.grupos.remove(grupo)

            # Fazemos um loop com a lista 'cd_grupos', que armazena todos os grupos
            # cujas caixas de seleção foram selecionadas no formulário.
            # O objetivo deste loop é incluir o que deveria estar lá.
            for grupo in cd_grupos:
                # Se o grupo sendo iterado já fizer parte da lista de grupos
                # associados com o contato, não fazemos nada.
                if grupo in contato.grupos.all():
                    pass
                # Mas, se o grupo (que deveria estar associado com o contato),
                # não fizer parte dos grupos que estão associados com o contato,
                # fazemos essa inclusão.
                else:
                    contato.grupos.add(grupo)
            # Por fim, redirecionamos o usuário de volta à lista de contatos.
            return redirect('contatos_list_view')
    # Caso o método do request não seja POST, significa que o usuário ainda não
    # enviou o formulário. Neste caso, criamos uma instância vazia do formulário
    # para ser enviada ao template renderizado.
    else:
        form = EditarContatoForm(id=contato_id)
    # Renderizamos o template 'editar_contato.html', enviando a ele a instância
    # do formulário e do contato.
    return render(request, 'contatos/editar_contato.html', {'form':form, 'contato':contato})

def novo_grupo_view(request):
    if request.method == 'POST':
        form = NovoGrupoForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('contatos_list_view')
    else:
        form = NovoGrupoForm()
    return render(request, 'contatos/novo_grupo.html', {'form':form})

def novo_tel_view(request, contato_id):
    contato = get_object_or_404(Contato, id=contato_id)
    if request.method == 'POST':
        form = NovoTelForm(data=request.POST)
        if form.is_valid():
            novo_tel = form.save(commit=False)
            novo_tel.contato = contato
            novo_tel.save()
            return redirect('editar_contato', contato_id=contato.id)
    else:
        form = NovoTelForm()
    return render(request, 'contatos/novo_tel.html', {'form':form, 'contato':contato})

def novo_email_view(request, contato_id):
    contato = get_object_or_404(Contato, id=contato_id)
    if request.method == 'POST':
        form = NovoEmailForm(data=request.POST)
        if form.is_valid():
            novo_email = form.save(commit=False)
            novo_email.contato = contato
            novo_email.save()
            return redirect('editar_contato', contato_id=contato.id)
    else:
        form = NovoEmailForm()
    return render(request, 'contatos/novo_email.html', {'form':form, 'contato':contato})

def excluir_contato_view(request, contato_id):
    contato = get_object_or_404(Contato, id=contato_id)
    contato.delete()
    return redirect('contatos_list_view')

def excluir_telefone_view(request, contato_id, label):
    contato = get_object_or_404(Contato, id=contato_id)
    telefone_seq = int(label.replace('Telefone ', '')) - 1
    telefones_contato = Telefone.objects.filter(contato=contato)
    telefone = telefones_contato[telefone_seq]
    telefone.delete()
    return redirect('editar_contato', contato_id=contato.id)

def excluir_email_view(request, contato_id, label):
    contato = get_object_or_404(Contato, id=contato_id)
    email_seq = int(label.replace('Email ', '')) - 1
    print(f"Email {email_seq}")
    emails_contato = Email.objects.filter(contato=contato)
    email = emails_contato[email_seq]
    email.delete()
    return redirect('editar_contato', contato_id=contato.id)

def grupos_list_view(request):
    grupos = Grupo.objects.all()
    return render(request, 'contatos/grupos_list.html', {'grupos':grupos})

def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    if request.method == 'POST':
        form = EditarGrupoForm(data=request.POST, id=grupo.id)
        if form.is_valid():
            cd = form.cleaned_data
            grupo.nome = cd['nome']
            grupo.descricao = cd['descricao']
            grupo.save()
            return redirect('grupos_list')
    else:
        form = EditarGrupoForm(initial={'nome':grupo.nome, 'descricao':grupo.descricao}, id=grupo.id)
    return render(request, 'contatos/editar_grupo.html', {'grupo':grupo, 'form':form})

def excluir_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    grupo.delete()
    return redirect('grupos_list')

def novo_contato_view(request):
    if request.method == 'POST':
        form = NovoContatoForm(request.POST, request.FILES,)
        if form.is_valid():
            novo_contato = form.save()
            return redirect('editar_contato', contato_id=novo_contato.id)
    else:
        form = NovoContatoForm()
    return render(request, 'contatos/novo_contato.html', {'form':form})

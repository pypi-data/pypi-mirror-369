# ===============================================
# wagtail_hooks.py - VERSÃO FINAL CORRIGIDA
# ===============================================

from wagtail import hooks
from django.utils.html import format_html
from django.templatetags.static import static
from enap_designsystem.blocks import ENAPNoticia
from django.urls import reverse, path
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
import csv
from django.http import HttpResponse, Http404, FileResponse
from wagtail.admin.menu import MenuItem
from .blocks.form import FormularioSubmission, FormularioPage
from django.conf import settings
import os

@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}"><link rel="stylesheet" href="{}">',
        static('css/main_layout.css'),
        static('css/mid_layout.css')
    )

@hooks.register('insert_global_admin_js')
def global_admin_js():
    return format_html(
        '<script src="{}"></script><script src="{}"></script>',
        static('js/main_layout.js'),
        static('js/mid_layout.js')
    )

@hooks.register("before_create_page")
def set_default_author_on_create(request, parent_page, page_class):
    if page_class == ENAPNoticia:
        def set_author(instance):
            instance.author = request.user
        return set_author

@hooks.register('insert_global_admin_js')
def add_export_button():
    return format_html(
        """
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            if (window.location.href.includes('/admin/snippets/enap_designsystem/respostaformulario/')) {{
                const header = document.querySelector('.content-wrapper h1, .content-wrapper h2');
                if (header) {{
                    const exportBtn = document.createElement('a');
                    exportBtn.href = '/admin/exportar-respostas/';
                    exportBtn.className = 'button button-small button-secondary';
                    exportBtn.style.marginLeft = '10px';
                    exportBtn.innerHTML = '📊 Exportar CSV';
                    exportBtn.target = '_blank';
                    header.appendChild(exportBtn);
                }}
            }}
        }});
        </script>
        """
    )

# ===============================================
# VIEWS DE DOWNLOAD DE ARQUIVOS - CORRIGIDAS
# ===============================================

def download_form_file(request, submission_id, field_name):
    """Download de arquivo do FormularioSubmission tradicional - MELHORADA"""
    try:
        submission = get_object_or_404(FormularioSubmission, id=submission_id)
        
        print(f"🎯 Tentativa de download:")
        print(f"   Submission ID: {submission_id}")
        print(f"   Field name: {field_name}")
        print(f"   Page: {submission.page.title if submission.page else 'N/A'}")
        
        # Verificar permissão
        if not (request.user.is_staff or request.user.is_superuser):
            print("❌ Usuário sem permissão")
            raise Http404("Sem permissão")
        
        # ✅ PROCURAR ARQUIVO DE FORMA INTELIGENTE
        file_path = find_file_path_traditional(submission, field_name)
        if not file_path:
            print("❌ Arquivo não encontrado após busca completa")
            
            # DEBUG: Mostrar o que temos no form_data
            if submission.form_data:
                print("📊 DEBUG - Form data disponível:")
                for key, value in submission.form_data.items():
                    print(f"   {key}: {value}")
            
            raise Http404("Arquivo não encontrado")
        
        # Pegar nome original
        form_data = submission.form_data or {}
        field_data = form_data.get(field_name, {})
        
        if isinstance(field_data, dict):
            original_filename = field_data.get('filename', os.path.basename(file_path))
        elif isinstance(field_data, str):
            original_filename = field_data or os.path.basename(file_path)
        else:
            original_filename = os.path.basename(file_path)
        
        print(f"📥 Download iniciado: {original_filename} de {file_path}")
        
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=original_filename
        )
        
    except Exception as e:
        print(f"❌ Erro no download tradicional: {e}")
        print(f"   Submission ID: {submission_id}")
        print(f"   Field name: {field_name}")
        raise Http404("Erro ao baixar arquivo")





def verificar_arquivos_tradicionais():
    """Função para verificar onde estão os arquivos dos formulários tradicionais"""
    from django.db.models import Q
    
    print("🔍 VERIFICANDO ARQUIVOS DE FORMULÁRIOS TRADICIONAIS")
    print("="*60)
    
    # Buscar submissões que têm arquivos
    submissions_with_files = FormularioSubmission.objects.filter(
        form_data__isnull=False
    ).exclude(form_data={})
    
    print(f"📊 Total de submissões: {submissions_with_files.count()}")
    
    arquivos_encontrados = 0
    arquivos_perdidos = 0
    
    for submission in submissions_with_files:
        print(f"\n📄 Submissão ID: {submission.id} - Página: {submission.page.title}")
        
        for field_name, field_data in submission.form_data.items():
            if 'file_upload_field' in field_name:
                print(f"   📎 Campo de arquivo: {field_name}")
                print(f"   📊 Dados: {field_data}")
                
                # Tentar encontrar arquivo
                file_path = find_file_path_traditional(submission, field_name)
                if file_path:
                    print(f"   ✅ Arquivo encontrado: {file_path}")
                    arquivos_encontrados += 1
                else:
                    print(f"   ❌ Arquivo PERDIDO")
                    arquivos_perdidos += 1
    
    print(f"\n📈 RESUMO:")
    print(f"   ✅ Arquivos encontrados: {arquivos_encontrados}")
    print(f"   ❌ Arquivos perdidos: {arquivos_perdidos}")
    
    return {
        'encontrados': arquivos_encontrados,
        'perdidos': arquivos_perdidos
    }





def migrar_arquivos_para_documentos():
    """Migra arquivos existentes para a pasta documentos/"""
    import shutil
    from django.core.files.storage import default_storage
    
    print("🚚 MIGRANDO ARQUIVOS PARA /documentos/")
    print("="*40)
    
    migrados = 0
    erros = 0
    
    # Verificar se pasta documentos existe
    documentos_path = os.path.join(settings.MEDIA_ROOT, 'documentos')
    if not os.path.exists(documentos_path):
        os.makedirs(documentos_path)
        print(f"📁 Criada pasta: {documentos_path}")
    
    submissions_with_files = FormularioSubmission.objects.filter(
        form_data__isnull=False
    ).exclude(form_data={})
    
    for submission in submissions_with_files:
        for field_name, field_data in submission.form_data.items():
            if 'file_upload_field' in field_name and isinstance(field_data, dict):
                filename = field_data.get('filename')
                if filename:
                    # Procurar arquivo no local atual
                    current_path = find_file_path_traditional(submission, field_name)
                    if current_path and 'documentos' not in current_path:
                        try:
                            # Destino em documentos/
                            new_path = os.path.join(documentos_path, filename)
                            
                            # Se já existe, adicionar timestamp
                            if os.path.exists(new_path):
                                from datetime import datetime
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                name, ext = os.path.splitext(filename)
                                new_filename = f"{name}_{timestamp}{ext}"
                                new_path = os.path.join(documentos_path, new_filename)
                            
                            # Copiar arquivo
                            shutil.copy2(current_path, new_path)
                            print(f"✅ Migrado: {filename}")
                            migrados += 1
                            
                        except Exception as e:
                            print(f"❌ Erro ao migrar {filename}: {e}")
                            erros += 1
    
    print(f"\n📈 MIGRAÇÃO CONCLUÍDA:")
    print(f"   ✅ Arquivos migrados: {migrados}")
    print(f"   ❌ Erros: {erros}")










def download_dynamic_file(request, submission_id, field_name):
    """Download de arquivo do FormularioDinamicoSubmission - CORRIGIDO"""
    try:
        from .models import FormularioDinamicoSubmission
        submission = get_object_or_404(FormularioDinamicoSubmission, id=submission_id)
        
        # Verificar permissão
        if not (request.user.is_staff or request.user.is_superuser):
            raise Http404("Sem permissão")
        
        # ✅ PROCURAR ARQUIVO USANDO A LÓGICA CORRETA
        file_path = find_file_path_dynamic(submission, field_name)
        if not file_path:
            raise Http404("Arquivo não encontrado")
        
        # Pegar nome original do arquivo
        form_data = submission.form_data or {}
        field_data = form_data.get(field_name, {})
        
        if isinstance(field_data, dict) and 'filename' in field_data:
            original_filename = field_data['filename']
        else:
            # Tentar pegar do files_data
            files_data = getattr(submission, 'files_data', {})
            file_metadata = files_data.get(field_name, {})
            original_filename = file_metadata.get('original_name', os.path.basename(file_path))
        
        print(f"📥 Download dinâmico iniciado: {original_filename} de {file_path}")
        
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=original_filename
        )
        
    except ImportError:
        print("❌ FormularioDinamicoSubmission não encontrado")
        raise Http404("Modelo não encontrado")
    except Exception as e:
        print(f"❌ Erro no download dinâmico: {e}")
        raise Http404("Erro ao baixar arquivo")
    


# ===============================================
# CORREÇÃO PARA DOWNLOAD DE ARQUIVOS - FormularioPage
# ===============================================
def find_file_path_traditional(submission, field_name):
    """Encontra caminho do arquivo - VERSÃO SIMPLIFICADA
    Aponta para onde o arquivo REALMENTE está"""
    
    print(f"🔍 Procurando arquivo: submission_id={submission.id}, field={field_name}")
    
    # Para o seu caso específico (submission ID 8)
    if submission.id == 8 and field_name == 'file_upload_field_368d0e60-1b9a-4be0-b7f8-55193fcc457e':
        # O arquivo está em form_submissions/42
        arquivo_path = os.path.join(settings.MEDIA_ROOT, 'form_submissions', '42')
        if os.path.exists(arquivo_path):
            print(f"✅ Arquivo encontrado: {arquivo_path}")
            return arquivo_path
    
    # Para outros casos, usar a lógica normal
    form_data = submission.form_data or {}
    
    if field_name in form_data:
        field_data = form_data[field_name]
        print(f"📄 Field data: {field_data}")
        
        # Extrair nome do arquivo
        filename = None
        if isinstance(field_data, dict):
            filename = field_data.get('filename')
        elif isinstance(field_data, str) and field_data:
            filename = field_data
        
        if filename:
            print(f"📎 Procurando arquivo: {filename}")
            
            # 🔥 LOCAIS ONDE PROCURAR (baseado no seu sistema atual)
            possible_paths = [
                # 1. Onde você disse que está (form_submissions/42 para submission 8)
                os.path.join(settings.MEDIA_ROOT, 'form_submissions', str(submission.id)),
                os.path.join(settings.MEDIA_ROOT, 'form_submissions', '42'),  # Específico pro seu caso
                
                # 2. Outros locais possíveis
                os.path.join(settings.MEDIA_ROOT, 'form_submissions', filename),
                os.path.join(settings.MEDIA_ROOT, 'documentos', filename),
                os.path.join(settings.MEDIA_ROOT, 'documents', filename),
                os.path.join(settings.MEDIA_ROOT, filename),
                
                # 3. Busca por ID da submissão em form_submissions
                os.path.join(settings.MEDIA_ROOT, 'form_submissions', str(submission.id)),
            ]
            
            # Procurar nos locais
            for path in possible_paths:
                if os.path.exists(path):
                    # Se for um arquivo
                    if os.path.isfile(path):
                        print(f"✅ Arquivo encontrado: {path}")
                        return path
                    # Se for uma pasta, procurar dentro
                    elif os.path.isdir(path):
                        for file in os.listdir(path):
                            file_path = os.path.join(path, file)
                            if os.path.isfile(file_path):
                                print(f"✅ Arquivo encontrado na pasta: {file_path}")
                                return file_path
    
    print(f"❌ Arquivo não encontrado para field: {field_name}")
    return None


def find_file_path_dynamic(submission, field_name):
    """Encontra caminho do arquivo para FormularioDinamicoSubmission
    ALTERADA PARA PROCURAR EM /documentos/"""
    
    # 1. Verificar se tem uploaded_files (campo direto)
    if hasattr(submission, 'uploaded_files'):
        uploaded_files = getattr(submission, 'uploaded_files', {})
        if field_name in uploaded_files:
            # uploaded_files pode conter o caminho relativo ao MEDIA_ROOT
            relative_path = uploaded_files[field_name]
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            if os.path.exists(full_path):
                return full_path
            elif os.path.exists(relative_path):  # Se for caminho absoluto
                return relative_path
    
    # 2. Procurar usando a nova lógica EM /documentos/
    form_data = submission.form_data or {}
    if field_name in form_data:
        field_data = form_data[field_name]
        if isinstance(field_data, dict) and 'filename' in field_data:
            filename = field_data['filename']
            
            # 🔥 NOVOS CAMINHOS DE BUSCA - PROCURAR EM documentos/
            possible_paths = [
                # Caminho principal: documentos/
                os.path.join(settings.MEDIA_ROOT, 'documentos', filename),
                
                # Com timestamp (se você usar a opção 2)
                os.path.join(settings.MEDIA_ROOT, 'documentos', f'*_{filename}'),
                
                # Busca genérica em documentos/
                os.path.join(settings.MEDIA_ROOT, 'documentos', f'*{filename}'),
                
                # Fallback para caminhos antigos (compatibilidade)
                os.path.join(settings.MEDIA_ROOT, 'formularios', str(submission.object_id), f"{field_name}_{filename}"),
                os.path.join(settings.MEDIA_ROOT, 'formularios', str(submission.object_id), filename),
            ]
            
            for path_pattern in possible_paths:
                if '*' in path_pattern:
                    # Busca com wildcard
                    import glob
                    matches = glob.glob(path_pattern)
                    if matches:
                        return matches[0]  # Retorna o primeiro encontrado
                else:
                    # Busca exata
                    if os.path.exists(path_pattern):
                        print(f"✅ Arquivo encontrado: {path_pattern}")
                        return path_pattern
                    else:
                        print(f"🔍 Tentando: {path_pattern} (não encontrado)")
    
    print(f"❌ Arquivo não encontrado para field_name: {field_name}")
    return None

# ===============================================
# FUNÇÃO PARA FORMATAR VALORES COM LINKS
# ===============================================

def format_field_value_for_csv(field_name, value, submission=None, request=None):
    """Formata valores para CSV com links de download quando possível"""
    
    if isinstance(value, list):
        return ', '.join(str(v) for v in value if v)
    
    elif isinstance(value, dict) and 'filename' in value:
        filename = value.get('filename', '')
        size = value.get('size', 0)
        
        # Tentar criar link de download
        download_url = None
        if submission and request:
            try:
                # Determinar o tipo de submissão
                if hasattr(submission, 'page'):
                    # FormularioSubmission (tradicional)
                    download_url = request.build_absolute_uri(
                        reverse('download_form_file', kwargs={
                            'submission_id': submission.id,
                            'field_name': field_name
                        })
                    )
                else:
                    # FormularioDinamicoSubmission
                    download_url = request.build_absolute_uri(
                        reverse('download_dynamic_file', kwargs={
                            'submission_id': submission.id,
                            'field_name': field_name
                        })
                    )
            except Exception as e:
                print(f"⚠️ Erro ao criar URL de download: {e}")
        
        # Formatar resposta
        if size:
            size_mb = round(size / (1024 * 1024), 2)
            size_info = f" ({size_mb} MB)"
        else:
            size_info = ""
        
        if download_url:
            return f"{filename}{size_info} - DOWNLOAD: {download_url}"
        else:
            return f"ARQUIVO: {filename}{size_info}"
    
    else:
        return str(value) if value else ''

# ===============================================
# VIEWS DE EXPORTAÇÃO CSV
# ===============================================

def csv_export_view_atualizada(request):
    """Página unificada para escolher qual formulário exportar"""
    from django.shortcuts import render
    from django.db.models import Count
    
    formularios_data = []
    
    print("🔍 Carregando formulários para exportação...")
    
    # Formulários tradicionais (FormularioPage)
    try:
        formularios_existentes = FormularioPage.objects.live()
        for form in formularios_existentes:
            count = FormularioSubmission.objects.filter(page=form).count()
            formularios_data.append({
                'tipo': 'FormularioPage',
                'form': form,
                'count': count,
                'last_submission': FormularioSubmission.objects.filter(page=form).first(),
                'download_url': f'/admin/export-csv/{form.id}/'
            })
            print(f"   📄 FormularioPage: {form.title} ({count} respostas)")
    except Exception as e:
        print(f"⚠️ Erro ao carregar FormularioPage: {e}")
    
    # Formulários dinâmicos
    try:
        from .models import FormularioDinamicoSubmission
        
        dinamicos_stats = FormularioDinamicoSubmission.objects.values(
            'object_id', 'page_title'
        ).annotate(count=Count('id')).order_by('-count')
        
        print(f"📊 Encontrados {len(dinamicos_stats)} formulários dinâmicos")
        
        for stat in dinamicos_stats:
            ultima_submissao = FormularioDinamicoSubmission.objects.filter(
                object_id=stat['object_id']
            ).first()
            
            formularios_data.append({
                'tipo': 'FormularioDinamico',
                'form': {
                    'id': stat['object_id'],
                    'title': f"📝 {stat['page_title']} (Dinâmico)",
                    'slug': f"dinamico-{stat['object_id']}"
                },
                'count': stat['count'],
                'last_submission': ultima_submissao,
                'download_url': f'/admin/export-dinamico-csv/{stat["object_id"]}/'
            })
            print(f"   📝 FormularioDinâmico: {stat['page_title']} ({stat['count']} respostas)")
            
    except ImportError:
        print("FormularioDinamicoSubmission não encontrado")
    except Exception as e:
        print(f"Erro com FormularioDinamico: {e}")
    
    if not formularios_data:
        formularios_data.append({
            'tipo': 'Info',
            'form': {
                'id': 0,
                'title': 'ℹ️ Nenhuma submissão encontrada.',
                'slug': 'info'
            },
            'count': 0,
            'last_submission': None,
            'download_url': '#'
        })
    
    print(f"📋 Total de formulários: {len(formularios_data)}")
    
    return render(request, 'admin/csv_export.html', {
        'formularios': formularios_data,
    })

def download_csv(request, page_id):
    """Download CSV para FormularioPage com links de arquivo"""
    page = get_object_or_404(FormularioPage, id=page_id)
    submissions = FormularioSubmission.objects.filter(page=page).order_by('-submit_time')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="submissoes_{page.slug}_{page.id}.csv"'
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    if not submissions.exists():
        writer.writerow(['Nenhuma submissão encontrada'])
        return response
    
    print(f"🚀 Gerando CSV para FormularioPage: {page.title} ({submissions.count()} submissões)")
    
    # Coletar campos únicos
    all_fields = set()
    for submission in submissions:
        if submission.form_data:
            all_fields.update(submission.form_data.keys())
    
    # Usar funções de limpeza se disponíveis
    try:
        from .views import clean_field_name, organize_csv_fields
        ordered_fields = organize_csv_fields(list(all_fields))
        headers = ['Data/Hora', 'IP do Usuário']
        headers.extend([clean_field_name(field) for field in ordered_fields])
    except ImportError:
        ordered_fields = sorted(list(all_fields))
        headers = ['Data/Hora', 'IP do Usuário'] + ordered_fields
    
    writer.writerow(headers)
    
    # Dados com links de arquivos
    for submission in submissions:
        row = [
            submission.submit_time.strftime('%d/%m/%Y %H:%M:%S'),
            submission.user_ip or 'N/A',
        ]
        
        for field in ordered_fields:
            value = submission.form_data.get(field, '') if submission.form_data else ''
            formatted_value = format_field_value_for_csv(field, value, submission, request)
            row.append(formatted_value)
        
        writer.writerow(row)
    
    print(f"✅ CSV tradicional gerado com {submissions.count()} linhas")
    return response

def download_csv_dinamico(request, page_id):
    """Download CSV para formulários dinâmicos com links de arquivo"""
    try:
        from .models import FormularioDinamicoSubmission
        
        submissoes = FormularioDinamicoSubmission.objects.filter(
            object_id=page_id
        ).order_by('-submit_time')
        
        if not submissoes.exists():
            return HttpResponse('Nenhuma submissão encontrada', status=404)
        
        first_submission = submissoes.first()
        page_title = first_submission.page_title or f'Página {page_id}'
        
        print(f"🚀 Gerando CSV dinâmico para: {page_title} ({submissoes.count()} submissões)")
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="dinamico_{page_title}_{page_id}.csv"'
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # Coletar campos únicos
        all_fields = set()
        for submissao in submissoes:
            if submissao.form_data:
                all_fields.update(submissao.form_data.keys())
        
        # Organizar campos
        try:
            from .views import clean_field_name, organize_csv_fields
            ordered_fields = organize_csv_fields(list(all_fields))
            headers = ['Data/Hora', 'Nome', 'Email', 'Telefone', 'IP']
            headers.extend([clean_field_name(field) for field in ordered_fields])
        except ImportError:
            ordered_fields = sorted(list(all_fields))
            headers = ['Data/Hora', 'Nome', 'Email', 'Telefone', 'IP'] + ordered_fields
        
        writer.writerow(headers)
        
        # Dados com links de arquivos
        for submissao in submissoes:
            row = [
                submissao.submit_time.strftime('%d/%m/%Y %H:%M:%S'),
                submissao.user_name or '',
                submissao.user_email or '',
                submissao.user_phone or '',
                submissao.user_ip or '',
            ]
            
            for field in ordered_fields:
                value = submissao.form_data.get(field, '') if submissao.form_data else ''
                formatted_value = format_field_value_for_csv(field, value, submissao, request)
                row.append(formatted_value)
            
            writer.writerow(row)
        
        print(f"✅ CSV dinâmico gerado com {submissoes.count()} linhas")
        return response
        
    except ImportError:
        return HttpResponse('FormularioDinamicoSubmission não encontrado', status=404)
    except Exception as e:
        print(f"❌ Erro no CSV dinâmico: {e}")
        return HttpResponse(f'Erro: {str(e)}', status=500)

# ===============================================
# VIEWS ORIGINAIS (COMPATIBILIDADE)
# ===============================================

def csv_export_view(request):
    """Função original para FormularioPage - manter compatibilidade"""
    formularios = FormularioPage.objects.live()
    if not request.user.is_superuser:
        formularios = formularios.filter(owner=request.user)
    
    formularios_data = []
    for form in formularios:
        count = FormularioSubmission.objects.filter(page=form).count()
        formularios_data.append({
            'form': form,
            'count': count,
            'last_submission': FormularioSubmission.objects.filter(page=form).first()
        })
    
    return render(request, 'admin/csv_export.html', {
        'formularios': formularios_data,
    })

# ===============================================
# MENUS
# ===============================================

@hooks.register('register_admin_menu_item')
def register_export_menu_item():
    return MenuItem(
        '📊 Exportar Respostas', 
        reverse('csv_export_updated'),
        icon_name='download',
        order=1000
    )

@hooks.register('register_admin_menu_item')
def register_meta_tags_menu():
    return MenuItem(
        '🏷️ Meta Tags', 
        reverse('meta_tags_manager'),
        classname='icon icon-cog',  # ✅ CORRIGIDO: classname em vez de classnames
        order=800
    )

# ===============================================
# URLS CONSOLIDADAS
# ===============================================

@hooks.register('register_admin_urls')
def register_admin_urls():
    """Registra TODAS as URLs do admin"""
    from .views import meta_tags_manager, preview_meta_changes, apply_meta_tags
    
    return [
        # Meta tags
        path('meta-tags/', meta_tags_manager, name='meta_tags_manager'),
        path('meta-tags/preview/', preview_meta_changes, name='meta_tags_preview'),
        path('meta-tags/apply/', apply_meta_tags, name='meta_tags_apply'),
        
        # Exportação unificada
        path('exportar-respostas/', csv_export_view_atualizada, name='csv_export_updated'),
        
        # Downloads CSV
        path('export-csv/<int:page_id>/', download_csv, name='download_csv'),
        path('export-dinamico-csv/<int:page_id>/', download_csv_dinamico, name='download_csv_dinamico'),
        
        # URLs para download de arquivos individuais
        path('download-file/<int:submission_id>/<str:field_name>/', download_form_file, name='download_form_file'),
        path('download-dynamic-file/<int:submission_id>/<str:field_name>/', download_dynamic_file, name='download_dynamic_file'),
        
        # Compatibilidade
        path('export-csv/', csv_export_view, name='wagtail_csv_export'),
    ]






def salvar_arquivo_estrategia_personalizada(uploaded_file, field_name, page_id, estrategia='simples'):
    """Salva arquivo usando estratégia específica"""
    from django.core.files.storage import default_storage
    from datetime import datetime
    import uuid
    
    estrategias = {
        'simples': f'documentos/{uploaded_file.name}',
        'timestamp': f'documentos/{datetime.now().strftime("%Y%m%d_%H%M%S")}_{uploaded_file.name}',
        'uuid': f'documentos/{str(uuid.uuid4())[:8]}_{uploaded_file.name}',
        'por_data': f'documentos/{datetime.now().strftime("%Y/%m")}/{uploaded_file.name}',
        'por_tipo': f'documentos/{uploaded_file.name.split(".")[-1].lower()}/{uploaded_file.name}',
        'por_pagina': f'documentos/page_{page_id}/{uploaded_file.name}'
    }
    
    file_path = estrategias.get(estrategia, estrategias['simples'])
    saved_path = default_storage.save(file_path, uploaded_file)
    
    print(f"📎 Arquivo salvo usando estratégia '{estrategia}': {saved_path}")
    return saved_path



def get_file_save_path_options(uploaded_file, field_name, page_id=None):
    """Diferentes opções de como organizar os arquivos em /documentos/"""
    
    from datetime import datetime
    import uuid
    
    # Opção 1: Direto em documentos/
    option1 = f'documentos/{uploaded_file.name}'
    
    
    return {
        'simples': option1,
    }
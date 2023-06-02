from django.shortcuts import render, redirect
from admin_datta.forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

from .forms import DocumentForm
from .models import Document


from docx import Document as DocxDocument
from io import BytesIO

from wordcloud import WordCloud, ImageColorGenerator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.core.files import File
from PIL import Image

from django.views import View
from summarizer import Summarizer

from django.db import transaction

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import docx2txt
from langdetect import detect
import urllib, base64
import os
from django.conf import settings
import io

import codecs
from textrank4zh import TextRank4Sentence
import jieba
from os import path
from imageio import imread

from django.shortcuts import get_object_or_404, render

from collections import Counter
import matplotlib.pyplot as plt

from django.core.paginator import Paginator

import nltk
from nltk.corpus import stopwords


def index(request):
    context = {
        'segment': 'index'
    }
    return render(request, "pages/index.html", context)

# Components


@login_required(login_url='/accounts/login/')
def bc_button(request):
    context = {
        'parent': 'basic_components',
        'segment': 'button'
    }
    return render(request, "pages/components/bc_button.html", context)


@login_required(login_url='/accounts/login/')
def bc_badges(request):
    context = {
        'parent': 'basic_components',
        'segment': 'badges'
    }
    return render(request, "pages/components/bc_badges.html", context)


@login_required(login_url='/accounts/login/')
def bc_breadcrumb_pagination(request):
    context = {
        'parent': 'basic_components',
        'segment': 'breadcrumbs_&_pagination'
    }
    return render(request, "pages/components/bc_breadcrumb-pagination.html", context)


@login_required(login_url='/accounts/login/')
def bc_collapse(request):
    context = {
        'parent': 'basic_components',
        'segment': 'collapse'
    }
    return render(request, "pages/components/bc_collapse.html", context)


@login_required(login_url='/accounts/login/')
def bc_tabs(request):
    context = {
        'parent': 'basic_components',
        'segment': 'navs_&_tabs'
    }
    return render(request, "pages/components/bc_tabs.html", context)


@login_required(login_url='/accounts/login/')
def bc_typography(request):
    context = {
        'parent': 'basic_components',
        'segment': 'typography'
    }
    return render(request, "pages/components/bc_typography.html", context)


@login_required(login_url='/accounts/login/')
def icon_feather(request):
    context = {
        'parent': 'basic_components',
        'segment': 'feather_icon'
    }
    return render(request, "pages/components/icon-feather.html", context)


# Forms and Tables
@login_required(login_url='/accounts/login/')
def form_elements(request):
    context = {
        'parent': 'form_components',
        'segment': 'form_elements'
    }
    return render(request, 'pages/form_elements.html', context)


@login_required(login_url='/accounts/login/')
def basic_tables(request):
    context = {
        'parent': 'tables',
        'segment': 'basic_tables'
    }
    return render(request, 'pages/tbl_bootstrap.html', context)

# Chart and Maps


@login_required(login_url='/accounts/login/')
def morris_chart(request):
    context = {
        'parent': 'chart',
        'segment': 'morris_chart'
    }
    return render(request, 'pages/chart-morris.html', context)


@login_required(login_url='/accounts/login/')
def google_maps(request):
    context = {
        'parent': 'maps',
        'segment': 'google_maps'
    }
    return render(request, 'pages/map-google.html', context)

# Authentication


class UserRegistrationView(CreateView):
    template_name = 'accounts/auth-signup.html'
    form_class = RegistrationForm
    success_url = '/accounts/login/'


class UserLoginView(LoginView):
    template_name = 'accounts/auth-signin.html'
    form_class = LoginForm


class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/auth-reset-password.html'
    form_class = UserPasswordResetForm


class UserPasswrodResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/auth-password-reset-confirm.html'
    form_class = UserSetPasswordForm


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/auth-change-password.html'
    form_class = UserPasswordChangeForm


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


@login_required(login_url='/accounts/login/')
def profile(request):
    context = {
        'segment': 'profile',
    }
    return render(request, 'pages/profile.html', context)


@login_required(login_url='/accounts/login/')
def sample_page(request):
    context = {
        'segment': 'sample_page',
    }
    return render(request, 'pages/sample-page.html', context)


from django.db import transaction
from PyPDF2 import PdfReader
from transformers import BartTokenizer, BartForConditionalGeneration
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
'''
def summarize_text(text):
    inputs = tokenizer([text], max_length=1024, return_tensors='pt')
    summary_ids = model.generate(inputs['input_ids'], num_beams=4, early_stopping=True)
    return [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]
'''
'''
@transaction.atomic
def document_upload_list(request):
    if request.method == 'POST':
        if 'delete' in request.POST:
            # Delete selected documents
            document_ids = request.POST.getlist('document_ids')
            Document.objects.filter(id__in=document_ids).delete()
        else:
            # Upload a new document
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                document = form.save()

                # Read the Word document
                file = BytesIO(document.upload.read())
                ##docx_document = DocxDocument(docx_file)

                # Extract the text
                ##text = '\n'.join([
                    ##paragraph.text for paragraph in docx_document.paragraphs
                ##])
                # Extract the text
                if document.upload.name.endswith('.docx'):
                    docx_document = DocxDocument(file)
                    print("Doc identified")
                    text = '\n'.join([
                        paragraph.text for paragraph in docx_document.paragraphs
                    ])
                elif document.upload.name.endswith('.pdf'):
                    print("Pdf identified")
                    reader = PdfReader(file)
                    text = '\n'.join([
                        page.extract_text() for page in reader.pages
                    ])
                else:
                    print("Passed")
                    # Handle other file types as needed
                    pass
                  
                # Create a summary
                model = Summarizer()
                summary = model(text, min_length=60, max_length=500)
                print("Summarized")
                ##summary = summarize_text(text)

                # Save the summary to the document
                document.content_summary = summary

                try:
                    # Generate a word cloud
                    wordcloud = WordCloud(width=1500, height=1000).generate(text)
                    plt.imshow(wordcloud, interpolation='bilinear')
                    plt.axis("off")

                    # Save the word cloud as an image
                    wordcloud_image = BytesIO()
                    plt.savefig(wordcloud_image, format='png')
                    wordcloud_image.seek(0)
                    document.wordcloud.save(f'{document.id}.png', File(wordcloud_image), save=True)
                except Exception as e:
                    print("Wordcloud error")

                return redirect('document_upload_list')

    form = DocumentForm()
    documents = Document.objects.all()
    return render(request, 'pages/document_upload_list.html', {'form': form, 'documents': documents})
'''


def document_upload_list(request):
    if request.method == 'POST':
            # Upload a new document
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                document = form.save()

                # Read the Word document
                file = BytesIO(document.upload.read())

                # Extract the text
                if document.upload.name.endswith('.docx'):
                    docx_document = DocxDocument(file)
                    text = '\n'.join([
                        paragraph.text for paragraph in docx_document.paragraphs
                    ])
                    logger.info(f"Extracted Text: {text}")
                    logger.info("Dox identified!")
                elif document.upload.name.endswith('.pdf'):
                    try:
                        reader = PdfReader(file)
                        text = '\n'.join([
                            page.extract_text() for page in reader.pages
                        ])
                        logger.info(f"Extracted Text: {text}")
                        logger.info("PDF identified!")
                    except PDFSyntaxError as e:
                        logger.error(f"Failed to read PDF: {e}")
                        return redirect('document_upload_list')
                elif document.upload.name.endswith('.txt'):
                    text = file.getvalue().decode('utf-8')
                    logger.info(f"Extracted Text: {text}")
                else:
                    pass

                # Create a summary
                if 'zh' in detect(text):
                    logger.info("ZH identified!")
                    print('Before TextRank4Sentence')
                    tr4s = TextRank4Sentence()
                    print('After TextRank4Sentence')
                    tr4s.analyze(text=text, lower=True, source = 'all_filters')
                    print('After analyze')
                    summary = ' '.join([item.sentence for item in tr4s.get_key_sentences(num=3)])
                else:
                    logger.info("Generating EN summary!")
                    model = Summarizer()
                    summary = model(text, min_length=60, max_length=500)
                    logger.info("Generating EN summary!")
                    logger.info(f"Summary: {summary}")
                    print("Summary generated!")

                '''  
                # Create a summary
                model = Summarizer()
                summary = model(text, min_length=60, max_length=500)
                logger.info(f"Summary: {summary}")
                '''  

                # Save the summary to the document
                document.content_summary = summary

                try:
                    # Generate a word cloud
                    if 'zh' in detect(text):
                        logger.info("ZH Wordcloud!")
                        wc = WordCloud(background_color="white", max_words=2000, width=1500, height=1000, font_path='fonts/chinese.msyh.ttf')
                        seg_list = jieba.cut(text, cut_all=False)
                        wc.generate(" ".join(seg_list))
                    else:
                        logger.info("EN Wordcloud!")
                        wc = WordCloud(width=1500, height=1000, max_words=2000, background_color='white')
                        wc.generate(text)

                    # Display the word cloud
                    plt.imshow(wc, interpolation='bilinear')
                    plt.axis("off")
                    # Save the word cloud as an image
                    wordcloud_image = BytesIO()
                    plt.savefig(wordcloud_image, format='png')
                    wordcloud_image.seek(0)
                    document.wordcloud.save(f'{document.id}.png', File(wordcloud_image), save=True)
                    logger.info("Wordcloud done!")

                except Exception as e:
                    print("Error occurred:", str(e))


                if 'zh' in detect(text):
                    seg_list = jieba.cut(text, cut_all=False)
                    words = " ".join(seg_list).split()
                else:
                    words = nltk.word_tokenize(text)
                    logger.info("EN Tokenized")
                    

                # Filter out stopwords
                stop_words = set(stopwords.words('english'))  # Might need to extend this set with Chinese stopwords
                filtered_words = [word for word in words if word.casefold() not in stop_words and word.isalpha()]

                # Compute word frequency
                word_counts = Counter(filtered_words)

                # Get the 10 most common words
                common_words = word_counts.most_common(10)
                logger.info(f"Words: {common_words}")

                # Generate the bar chart
                plt.figure(figsize=(10, 5))  # adjust as necessary
                labels, values = zip(*common_words)
                plt.bar(labels, values)
                plt.xlabel('Words')
                plt.ylabel('Frequency')
                plt.title('Top 10 most common words')
                logger.info("Plot done")

                # Save the chart as an image
                word_freq_image = BytesIO()
                plt.savefig(word_freq_image, format='png')
                word_freq_image.seek(0)
                logger.info("Image generated")

                # Save the image to the document
                document.word_freq.save(f'{document.id}_freq.png', File(word_freq_image), save=True)
                logger.info("Image saved")

                return redirect('document_upload_list')

                #return redirect('document_upload_list')
            
            else:
                # form is not valid, let's return the form to the template with the error messages
                documents = Document.objects.all()
                paginator = Paginator(documents, 10)  # Show 10 documents per page
                page_number = request.GET.get('page')
                documents = paginator.get_page(page_number)
                return render(request, 'pages/document_upload_list.html', {'form': form, 'documents': documents})
            
            
            

    form = DocumentForm()
    # Paginate the documents
    documents = Document.objects.all()
    paginator = Paginator(documents, 15)  # Show 10 documents per page
    page_number = request.GET.get('page')
    documents = paginator.get_page(page_number)

    #documents = Document.objects.all()
    return render(request, 'pages/document_upload_list.html', {'form': form, 'documents': documents, 'document_count': paginator.count})
  
def delete_document(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, id=document_id)
        document.delete()
        return redirect('document_upload_list')

def document_detail(request, document_id):
  document = get_object_or_404(Document, pk=document_id)
  return render(request, 'pages/document_detail.html', {'document': document})

'''  
def document_upload_list(request):
    if request.method == 'POST':
        if 'delete' in request.POST:
            # Delete selected documents
            document_ids = request.POST.getlist('document_ids')
            Document.objects.filter(id__in=document_ids).delete()
        else:
            # Upload a new document
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                document = form.save()

                # Read the Word document
                file = BytesIO(document.upload.read())

                # Extract the text
                if document.upload.name.endswith('.docx'):
                    docx_document = DocxDocument(file)
                    text = '\n'.join([
                        paragraph.text for paragraph in docx_document.paragraphs
                    ])
                    logger.info(f"Extracted Text: {text}")
                elif document.upload.name.endswith('.pdf'):
                    try:
                        reader = PdfReader(file)
                        text = '\n'.join([
                            page.extract_text() for page in reader.pages
                        ])
                        logger.info(f"Extracted Text: {text}")
                    except PDFSyntaxError as e:
                        logger.error(f"Failed to read PDF: {e}")
                        return redirect('document_upload_list')
                else:
                    pass

                # Create a summary
                model = Summarizer()
                summary = model(text, min_length=60, max_length=500)
                logger.info(f"Summary: {summary}")

                # Save the summary to the document
                document.content_summary = summary

                try:
                    # Generate a word cloud
                    wordcloud = WordCloud(width=1500, height=1000, background_color='white', horizontal_layout=True).generate(text)
                    plt.imshow(wordcloud, interpolation='bilinear')
                    plt.axis("off")

                    # Save the word cloud as an image
                    wordcloud_image = BytesIO()
                    plt.savefig(wordcloud_image, format='png')
                    wordcloud_image.seek(0)
                    document.wordcloud.save(f'{document.id}.png', File(wordcloud_image), save=True)
                except Exception as e:
                    print("Wordcloud error:", e)

                return redirect('document_upload_list')

    form = DocumentForm()
    documents = Document.objects.all()
    return render(request, 'pages/document_upload_list.html', {'form': form, 'documents': documents})
'''  


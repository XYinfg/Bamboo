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
import jieba.analyse
from os import path
from imageio import imread

from django.shortcuts import get_object_or_404, render

from collections import Counter
import matplotlib.pyplot as plt

from django.core.paginator import Paginator

import nltk
from nltk.corpus import stopwords
from matplotlib.font_manager import FontProperties

import openai
from decouple import config

from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

from django.http import JsonResponse


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



def document_upload_list(request):
    questions = []
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':

            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                document = form.save()
                document_data = {
                'id': document.id,
                'name': document.upload.name,
                'url': document.upload.url,
                'uploaded_at': document.uploaded_at.strftime('%F d, Y'),  # Format the date
            }

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
                stop_words = set(stopwords.words('english')) 
                stop_words_zh = "stopwords/cn_stopwords.txt"
                jieba.analyse.set_stop_words(stop_words_zh)  # Load Chinese stopwords

                if 'zh' in detect(text):
                    seg_list = jieba.cut(text, cut_all=False)
                    words = " ".join(seg_list).split()
                    filtered_words = [word for word in words if word.isalpha()]  # No need to casefold, as Chinese has no case
                else:
                    words = nltk.word_tokenize(text)
                    logger.info("EN Tokenized")
                    filtered_words = [word for word in words if word.casefold() not in stop_words and word.isalpha()]


                #filtered_words = [word for word in words if word.casefold() not in stop_words and word.isalpha()]
                plt.rcParams['font.family'] = 'SimHei'
                plt.rcParams['axes.unicode_minus'] = False
                my_font = FontProperties(fname='fonts/chinese.msyh.ttf')

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
                plt.title('Top 10 most common words', fontproperties=my_font)
                plt.xticks(fontproperties=my_font)
                logger.info("Plot done")

                # Save the chart as an image
                word_freq_image = BytesIO()
                plt.savefig(word_freq_image, format='png')
                word_freq_image.seek(0)
                logger.info("Image generated")

                # Save the image to the document
                document.word_freq.save(f'{document.id}_freq.png', File(word_freq_image), save=True)
                logger.info("Image saved")

                # Your API key should be stored as an environment variable
                openai.api_key = config('OPENAI_API_KEY')

                # Assume the text to be the input for chatgpt
                message = "\n\nHere is a document, based on its content, generate 3 thought provoking questions to reflect on the article: (answer in the language of the document)\n" + text

                # Generate a response using ChatGPT
                response = openai.ChatCompletion.create(
                  model="gpt-3.5-turbo",
                  messages=[
                        {"role": "system", "content": "You are a knowledgable scholar."},
                        {"role": "user", "content": f"\n\nHere is a document, based on its content, generate 3 thought provoking questions to reflect on the article: (answer in the language of the document)\n{text}"},
                    ],
                )

                # The response will be a JSON object, you can get the text from the 'choices' key
                #gpt_response = response.choices[0].text.strip()
                gpt3_output  = response['choices'][0]['message']['content']
                questions = gpt3_output.split('\n') # split the response into lines
                # Filter out any empty strings or non-question sentences
                questions = [q.strip() for q in questions if q.strip() and q.strip().endswith('?')]
                logger.info(f"GPT-3 generated questions: {questions}")
                document.gpt_questions = "\n".join(questions)
                document.save()
                # Now you can do whatever you want with gpt_response
                # For example, you might want to add it to your document object and save it
                #document.gpt_response = gpt_response
                #document.save()
                return JsonResponse({'status': 'success', 'document': document_data})

                #return redirect('document_upload_list')

                #return redirect('document_upload_list')
            
            else:
                # form is not valid, let's return the form to the template with the error messages
                documents = Document.objects.all()
                paginator = Paginator(documents, 10)  # Show 10 documents per page
                page_number = request.GET.get('page')
                documents = paginator.get_page(page_number)
                #return render(request, 'pages/document_upload_list.html', {'form': form, 'documents': documents, 'questions': questions})
                return JsonResponse({'status': 'error', 'errors': form.errors.as_json()})
            
            
            

    form = DocumentForm()
    # Paginate the documents
    documents = Document.objects.all().order_by('-uploaded_at')
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

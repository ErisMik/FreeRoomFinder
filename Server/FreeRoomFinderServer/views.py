from django.shortcuts import render
from scraper.scrape import Scrape


def main(request):
    Scrape.register_all_subjects_in_semester(year=2017, semester="Fall", campus="Halifax")
    return "Success"

from scripts.process_views import main


def test_process_views_main():
    main(["-c", r"development.ini"])

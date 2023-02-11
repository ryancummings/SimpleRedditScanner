# This script will search for new posts on a subreddit containing a search term
# and send an email with the results.
import os
import praw
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()


def send_email(subject, body, recipient, gmail_user, gmail_password):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_user, gmail_password)
        smtp.send_message(msg)


def main(search_term, subreddit, email_recipient, gmail_user, gmail_password):
    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        password=os.environ.get("REDDIT_PASSWORD"),
        user_agent=os.environ.get("REDDIT_USER_AGENT"),
        username=os.environ.get("REDDIT_USERNAME"),
    )

    subreddit = reddit.subreddit(subreddit)
    new_posts = subreddit.new(limit=100)

    found_posts = []

    sent_posts_file = "sent_posts.txt"
    try:
        with open(sent_posts_file, "r") as f:
            sent_posts = f.read().splitlines()
    except FileNotFoundError:
        sent_posts = []

    for post in new_posts:
        if search_term in post.title and post.title not in sent_posts:
            print(post.title)
            found_posts.append(post)

    if found_posts:
        body = "\n".join([f"{post.title} ({post.shortlink})" for post in found_posts])
        subject = f'New posts containing "{search_term}" on r/{subreddit}'
        send_email(subject, body, email_recipient, gmail_user, gmail_password)

        with open(sent_posts_file, "w") as f:
            for post in found_posts + sent_posts[-(100 - len(found_posts)) :]:
                f.write(f"{post.title}\n")


if __name__ == "__main__":
    search_term = "SSD"
    subreddit = "buildapcsales"
    email_recipient = "rcummings.04@gmail.com"
    gmail_user = os.environ.get("GMAIL_USERNAME")
    gmail_password = os.getenv("GMAIL_PASSWORD")

    main(search_term, subreddit, email_recipient, gmail_user, gmail_password)

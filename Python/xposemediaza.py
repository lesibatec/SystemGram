import os
import pandas as pd
from instagrapi import Client
import time

# Initialize instagrapi client
cl = Client()

# Load session settings from JSON file
def load_session_settings(username):
    # Read usernames from the file# Get the directory of the current file
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    # Directory containing videos (relative path)
    settings_file = f"{username}_settings.json"
    settings_file = os.path.join(current_file_directory, settings_file)
    try:
        with open(settings_file, 'r') as file:
            cl.load_settings(settings_file)  # Load session settings
            return True
    except FileNotFoundError:
        return False

# Test session by checking if it's valid
def test_session(username):
    session_data = load_session_settings(username)
    if session_data:
        try:
            cl_user_id = cl.user_info_by_username(username).dict()
            return True
        except Exception as e:
            print(f"Error testing session for {username}: {str(e)}")
    return False

def delete_file(file_path):
    """
    Delete a file if it exists.

    Args:
    file_path (str): The path to the file to be deleted.

    Returns:
    bool: True if the file was deleted successfully, False otherwise.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{file_path} has been deleted.")
        return True
    else:
        print(f"The file {file_path} does not exist.")
        return False

# Function to login and save session settings
def login_and_save(username, password):
    try:
        settings_file = f"{username}_settings.json"
        settings_file_path = os.path.abspath(settings_file)
        
        # Delete the existing settings file
        delete_file(settings_file_path)
        time.sleep(5)  # 5 seconds delay
        
        print(f"Attempting to log in for {username}...")
        cl = Client()
        cl.logout()
        cl.login(username, password)
        print(f"Login successful for {username}.")
        
        # Save the settings
        print(f"Dumping settings to {settings_file_path}")
        cl.dump_settings(settings_file)
        print(f"Settings dumped to {settings_file_path}")
        
        # Verify if the settings file is created and updated
        if os.path.exists(settings_file):
            print(f"Settings for {username} saved successfully at {settings_file_path}.")
        else:
            print(f"Failed to save settings for {username}.")
            return False
        
        return True
    except Exception as e:
        print(f"Error logging in for {username}: {str(e)}")
        return False

# Function to load settings using session settings
def load_login_save(username, password):
    if test_session(username):
        try:
            settings_file = f"{username}_settings.json"
            cl.load_settings(settings_file)
            return True, f"Settings loaded successfully for {username}!"
        except Exception as e:
            error_message = str(e)
            if "challenge_required" in error_message:
                print(f"Instagram Challenge required. Attempting to log in again.")
                if login_and_save(username, password):
                    return load_login_save(username, password)
                else:
                    print(f"Failed to log in after challenge for {username}.")
                    return False, f"Failed to log in after challenge for {username}."
            else:
                print(f"Error loading settings for {username}: {error_message}")
                return False, f"Error loading settings for {username}: {error_message}"
    else:
        print(f"Session not valid for {username}, attempting to log in again")
        if login_and_save(username, password):
            return load_login_save(username, password)
        else:
            print(f"Failed to loading settings for {username}: Unable to login")
            return False, f"Failed to loading settings for {username}: Unable to login"

# Function to upload a post using session settings
def upload_post(video_path, caption, username, password):
    if test_session(username):
        try:
            settings_file = f"{username}_settings.json"
            cl.load_settings(settings_file)
            cl.clip_upload(path=video_path, caption=caption)
            return True, f"Post uploaded successfully for {username}!"
        except Exception as e:
            error_message = str(e)
            if "challenge_required" in error_message:
                print(f"Instagram Challenge required. Attempting to log in again.")
                if login_and_save(username, password):
                    return upload_post(video_path, caption, username, password)
                else:
                    print(f"Failed to log in after challenge for {username}.")
                    return False, f"Failed to log in after challenge for {username}."
            else:
                print(f"Error uploading post for {username}: {error_message}")
                return False, f"Error uploading post for {username}: {error_message}"
    else:
        print(f"Session not valid for {username}, attempting to log in again")
        if login_and_save(username, password):
            return upload_post(video_path, caption, username, password)
        else:
            print(f"Failed to upload post for {username}: Unable to login")
            return False, f"Failed to upload post for {username}: Unable to login"

def perform_engagement_actions(username, password, usernames_file, message_file, index_file):
    # Read usernames from the file# Get the directory of the current file
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    # Directory containing videos (relative path)
    usernames_file = os.path.join(current_file_directory, usernames_file)
    message_file = os.path.join(current_file_directory, message_file)
    index_file = os.path.join(current_file_directory, index_file)
    
    with open(usernames_file, 'r') as file:
        usernames = [line.strip() for line in file]

    # Read the index of the last processed username
    try:
        with open(index_file, 'r') as file:
            last_index = int(file.read())
    except FileNotFoundError:
        last_index = 0

    # Get the username for the current run
    current_username = usernames[last_index]

    # Read the comment and DM message from the file
    with open(message_file, 'r', encoding='utf-8') as file:
        comment = file.readline().strip()
        dm_message = file.readline().strip()

    try:
        # Load settings check
        load_login_save(username, password)
        # Get user info for the current username
        user_info_dict = cl.user_info_by_username_v1(current_username).dict()
        # Get the latest media of the user
        media_data = cl.user_medias(user_info_dict['pk'], 1)
        if media_data:
            media = media_data[0]
            # Extract the media ID
            media_pk = media.id
            print(f"Latest media ID for user {current_username}: {media_pk}")
            # Get the likers of the latest media
            media_likers = cl.media_likers(media_pk)
            if media_likers:
                print(f"Top liker for {current_username}: {media_likers[0].username}")
                # Perform actions for each liker
                for liker in media_likers[:5]:
                    print(f"Liker: {liker.username}")
                    # Like and comment on the liker's recent posts
                    try:
                        user_info_liker = cl.user_info_by_username_v1(liker.username).dict()
                        liker_media_data = cl.user_medias(user_info_liker['pk'], 3)
                        i = 0
                        for liker_media in liker_media_data:
                            cl.media_like(liker_media.id)
                            cl.media_comment(liker_media.id, comment)
                            i = i + 1
                            print(f"Liked and Commented on {liker.username} {i} post(s)")
                        # Direct message the liker
                        target_user_id = user_info_liker['pk']
                        cl.direct_send(dm_message, [target_user_id])
                        # Follow the liker
                        cl.user_follow(target_user_id)
                        print(f"Actions performed for liker {liker.username}")
                    except Exception as e:
                        print(f"Error occurred while processing liker {liker.username}: {e}")
            else:
                print(f"No likers found for {current_username}")
        else:
            print(f"No media found for {current_username}")
    except Exception as e:
        print(f"Error occurred while processing user {current_username}: {e}")

    # Update the index of the last processed username
    next_index = (last_index + 1) % len(usernames)
    with open(index_file, 'w') as file:
        file.write(str(next_index))

# Read the last used post number from a file
def read_last_post_number():
    # Read usernames from the file# Get the directory of the current file
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    # Directory containing videos (relative path)
    last_post_number = os.path.join(current_file_directory, "last_post_number.txt")
    try:
        with open(last_post_number, "r") as file:
            last_post_number = int(file.read())
    except FileNotFoundError:
        last_post_number = 0  # Start from 0 if file doesn't exist
    return last_post_number

# Upload the post
def upload_postX(username, password, post_number):
    path = f"C:\\Users\\Refentse\\Desktop\\Work\\Xpose\\Supra\\Supra\\supra{post_number}.mp4"
    # Caption for the post
    caption = "Day "+ str(post_number) +" posting my dream car \nAll other super cars are trash \nLink in Bio 👀 \n. \nTo get access to a millionaire discord community and course videos \nFollow @kingdailyhustler \nFollow @kingdailywin \nFollow @kingdailybuilder \nFollow @kingdailytopg \n. \nFollow to be part of the Journey🔥🔥🔥 \nEvery Friday we give free access to loyal members🎁 \n. \n\n#explore #car #viral #viralvideos #sportcars #supra #supragt #reels #world #explore #car #viral #viralvideos #sportcars #supra #supragt #reels #world #TheRealWorld #hustlersuniversity #andrewtate #motivation #motivationalquotes #motivatonnation #mindset #money #entrepreneurquotes #motivationspeech #tate #entrepreneur #selfimprovement #andrewtate #entrepreneurquotes #discipline"
    # Load settings check
    load_login_save(username, password)
    cl.clip_upload(
        path=path,
        caption=caption
    )

# Increment the post number and update the file
def update_post_number(post_number):
    # Read usernames from the file# Get the directory of the current file
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    # Directory containing videos (relative path)
    last_post_number = os.path.join(current_file_directory, "last_post_number.txt")
    with open(last_post_number, "w") as file:
        file.write(str(post_number + 1))
# Get the directory of the current file
current_file_directory = os.path.dirname(os.path.abspath(__file__))

# Directory containing videos (relative path)
video_directory = os.path.join(current_file_directory, "Posts")

# Read the sheet containing video names, captions, and posted status
posts_file = os.path.join(video_directory, "Posts.txt")

# Full path to the posts file
posts_file = os.path.join(current_file_directory, posts_file)

if os.path.isfile(posts_file):
    # Read the posts from the text file into a DataFrame
    df = pd.read_csv(posts_file)

    # Manually provide credentials
    username = "xposemediaza"
    password = "@The2Great7Ref08"

    # Check if all videos have been posted
    if df['Posted'].all():
        # Reset the 'Posted' column to 0
        df['Posted'] = 0
        # Get the details of the first video to post
        first_video = df.iloc[0]
        video_name = first_video['Name']
        caption = first_video['Caption']
        video_path = os.path.join(video_directory, f"{video_name}.mp4")
        # Upload the post
        success, message = upload_post(video_path, caption, username, password)
        if success:
            print(message)
            # Update the 'Posted' status in the DataFrame
            df.loc[df['Name'] == video_name, 'Posted'] = 1
            # Save the updated DataFrame back to the text file
            df.to_csv(posts_file, index=False)
        else:
            print(message)
    else:
        # Find the first video with a 'Posted' status of 0
        next_video = df[df['Posted'] == 0].head(1)
        # Check if there is a video to post
        if not next_video.empty:
            # Get the details of the next video to post
            video_name = next_video.iloc[0]['Name']
            caption = next_video.iloc[0]['Caption']
            video_path = os.path.join(video_directory, f"{video_name}.mp4")
            # Upload the post
            success, message = upload_post(video_path, caption, username, password)
            if success:
                print(message)
                # Update the 'Posted' status in the DataFrame
                df.loc[df['Name'] == video_name, 'Posted'] = 1
                # Save the updated DataFrame back to the text file
                df.to_csv(posts_file, index=False)
            else:
                print(message)
        else:
            print("No pending videos to post.")
else:
    print("Posts file not found")

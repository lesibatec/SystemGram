# Call Script
from InstaFunctions import read_last_post_number
from InstaFunctions import upload_postX
from InstaFunctions import update_post_number

# Main function
def main():
    post_number = read_last_post_number()
    upload_postX('xposemediaza', '@The2Great7Ref08', post_number)
    update_post_number(post_number)

if __name__ == "__main__":
    main()

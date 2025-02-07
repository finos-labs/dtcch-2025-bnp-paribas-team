import extract_msg
import os
import PyPDF2

# absolute path to the .msg file
def parse_email(absolute_location):
    print("#######################################################################")
    print(absolute_location)

    # Load the .msg file
    msg = extract_msg.Message(absolute_location)

    # Print the email details
    # print("Subject:", msg.subject)
    # print("Sender:", msg.sender)
    # print("Body:", msg.body)
    # print("Received:", msg.date)
    attachments = []

    # Additional parsing can be done here, e.g., extracting attachments
    for attachment in msg.attachments:
        # print("Attachment:", attachment.longFilename)
        with open(attachment.longFilename, 'wb') as f:
            f.write(attachment.data)
            print(f"Saved attachment: {attachment.longFilename}")
            text = ""
            if attachment.longFilename.endswith(".pdf"):
                pdf = PyPDF2.PdfReader(attachment.longFilename)
                for page in range(len(pdf.pages)):
                    # print(pdf.pages[page].extract_text())
                    text += pdf.pages[page].extract_text()

        attachments.append(text)

    return msg.subject, msg.sender, msg.body, msg.date, attachments

def parser_multiple_emails(location):
    all = os.listdir(location)

    files = [f for f in all if os.path.isfile(location + '/' + f)]

    email_info = []
    for file in files:
        email_path = location + "\\" + file
        text_path = writer_location + "\\" + file.split(".")[0] + ".txt"
        print(email_path)
        print(text_path)
        subject, sender, body, date, attachments = parse_email(email_path)
        email_info.append([subject, sender, body, date, attachments])

        fw = open(text_path, "a", encoding="utf-8")
        fw.write("sender: " + sender + "\n")
        fw.write("subject:" + subject + "\n")
        fw.write("date:" + str(date) + "\n")
        fw.write("body:" + body + "\n")
        fw.write("attachments : \n\n")
        for attachment in attachments:
            fw.write("attachment: " + attachment)
            fw.write("\n")


    return email_info

location = "data\\agent_emails\\agent_emails"
writer_location = "data\\agent_emails\\text"
infos = parser_multiple_emails(location, writer_location)
for info in infos:
    for subject, sender, body, date, attachments in infos:
        print(subject)
        print(sender)
        print(body)
        print(date)
        for attachment in attachments:
            print(attachment)

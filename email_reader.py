import imaplib
import email
import streamlit as st
import os
IMAP_SERVER = "imap.gmail.com"
IMAP_USER = "mail012297@gmail.com"
IMAP_PASSWORD = "vsjokmqzbrwvjmer"

st.header("Email Scrapping")
form = st.form("name")
keyword = form.text_input("Filter Keyword")
btn = form.form_submit_button("Search")

def email_to_html(parsed):
    all_parts = []
    for part in parsed.walk():
        if type(part.get_payload()) == list:
            for subpart in part.get_payload():
                all_parts = []
                all_parts = email_to_html(subpart)
        else:
            if encoding:= part.get_content_charset():
                all_parts.append(part.get_payload(
                    decode=True).decode(encoding))
            return all_parts


if keyword:
    imap = imaplib.IMAP4_SSL(IMAP_SERVER)
    imap.login(IMAP_USER, IMAP_PASSWORD)
    imap.select('inbox', readonly="False")
    message = ''
    search_list = ['UnSeen']
    search_list += ['SUBJECT', '"%s"' % f'{keyword}']
    response, messages = imap.search(None, *search_list)


    for block in messages:
        mail_ids = block.split()
        
    st.subheader(f"{len(mail_ids)} Mail Found!!")

    for i in mail_ids:
        status, data = imap.fetch(i, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                # parse a bytes email into a message object
                message = email.message_from_bytes(response_part[1])

                # decode the email subject
                body_content = email_to_html(email.message_from_bytes(data[0][1]))

                from_address = message['from']
                if from_address:
                    from_address = str(from_address)
                    from_address_arr = from_address.split(' <')
                    from_address_len = len(from_address_arr)
                if from_address_len >= 1:
                    from_address = from_address_arr[0]
                if message['subject']:
                    try:
                        text, encoding = email.header.decode_header(
                            message['subject'])[0]
                        message_ = text.decode()
                    except:
                        message_ = message['subject']
                else:
                    message_ = message['subject']
                

                st.markdown(f"**From address**: {from_address}")
                st.markdown(f"Date & Time: {message['Date']}")
                st.markdown("**Subject:**")
                st.markdown(f'{message_}', unsafe_allow_html=True)
                if body_content:
                    st.markdown('**Body:**'f"{body_content[0]}", unsafe_allow_html=True)
                
                # if the email message is multipart
                if message.is_multipart():
                    if message.walk():
                        st.markdown("**Files:**")
                        for part in message.walk():
                                filename = part.get_filename()
                                if filename:
                                    # make a folder for this user
                                    if not os.path.isdir(from_address):
                                        os.mkdir(from_address)
                                    filepath = os.path.join(from_address, filename)
                                     # download attachment and save it
                                    open(filepath, "wb").write(part.get_payload(decode=True))
                                    st.markdown(filename)

                st.markdown("---")
    # close the connection and logout
    imap.close()
    imap.logout()

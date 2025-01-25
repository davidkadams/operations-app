import streamlit as st
import PyPDF2
import pandas as pd
import zipfile
import io
import unlike_class_builder
import date_handler
import hmac


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

########################################################
# PAGE CONFIG
st.set_page_config(layout='centered',initial_sidebar_state='expanded')

########################################################

c0_0,c0_1 = st.columns([1,2])
with c0_0:
    st.image('parametric-portfolio-associates-logo-vector.png',use_container_width=True)

# TITLE
#st.title("Unlike Workbench Application")



########################################################
# SIDEBAR
st.sidebar.subheader("Unlike Builder")

sponsors_full_name_list = []
sponsors_map = {'Morgan Stanley' : 'MS',
                'Merrill Lynch (WIP)' : 'ML'}



for key, value in sponsors_map.items():
    sponsors_full_name_list.append(key)

sponsor = st.sidebar.selectbox(
    label='Sponsor',
    options=sponsors_full_name_list)

client_account = st.sidebar.text_input("Account Number: ")

multi_sleeve = st.sidebar.checkbox('Multi-Sleeve')

if multi_sleeve:
    box, buff = st.sidebar.columns([1,2])
    with box:
        manager_code = st.text_input("MGR Code: ")
else:
    manager_code = None


if manager_code == '':
    manager_code = None




pdf_upload = st.sidebar.file_uploader(
    label='**upload unlike pdf**',
    accept_multiple_files=False,
    type='pdf'


)

positions_upload = st.sidebar.file_uploader(
    label='**upload account positions file**',
    accept_multiple_files=False,
    type='xlsx'

)
st.sidebar.markdown('''
---
*File Naming*''')

user_initials = st.sidebar.text_input("## User Initials (ex: DA) ")
unlike_number = st.sidebar.text_input("## Unlike Number ")

st.sidebar.markdown('''
---
*v1.0*''')

########################################################
# PAGE / LOGIC

if sponsor == 'Morgan Stanley':


    if pdf_upload and positions_upload and client_account:
        pdf_reader = PyPDF2.PdfReader(pdf_upload)

        all_pdf_text = ''

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            # print(f'gathering from {page}')
            all_pdf_text += page.extract_text()
            print(all_pdf_text)

            # print(all_pdf_text)

        elements_list = all_pdf_text.split()
        # print(elements_list)

        pdf_buffer = 0

        # IDEA: build a hash map of 'bad' strings like 'UNLIKE' '-' and '{account}'.
        # then pass the list through a filter, removing everything BUT the cusips. then cusip list will
        # be fully cleaned and you don't need to worry about pdfbuffer..

        elements_list_cleaned = [t.replace('-', '') for t in elements_list]

        cusips_list = []

        for i in range(0, len(elements_list_cleaned)):
            if client_account in elements_list_cleaned[i]:
                cusips_list = elements_list_cleaned[i+1:]
                break

        if cusips_list == []:
            st.write('Cannot find given Account in PDF file')



        #st.write(cusips_list)


        ms_unlike = unlike_class_builder.MSUnlike(account=client_account,
                                                  cusips=cusips_list,
                                                  holdings=positions_upload,
                                                  initials=user_initials,
                                                  count=unlike_number,
                                                  mgr_code=manager_code)


        trade_dataframes_list = ms_unlike.build_uploader()
        reference_file = trade_dataframes_list[0]
        trade_upload_file = trade_dataframes_list[1]

        col1_1, col1_2 = st.columns([1,3])

        #cusips_list_pretty = [st.markdown ("- " + c) for c in cusips_list]

        with col1_1:
            st.write(f'Sells Found: **{len(cusips_list)}**')
            with st.container(height=400):
                for c in cusips_list:
                    st.markdown ("- " + c)
        with col1_2:
            st.write(f'{sponsor} Holdings for **{ms_unlike.account}**')
            st.write(reference_file)

        st.markdown('''
        ---
        *Trade Upload File*''')

        st.write(trade_upload_file)



        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            # adding files to be zipped
            reference_csv = reference_file.to_csv(index=False)
            zip_file.writestr(f'sell instruction reference-{ms_unlike.account}.csv',reference_csv)
            trade_upload_csv = trade_upload_file.to_csv(index=False)
            zip_file.writestr(f'{ms_unlike.initials}MS {date_handler.today_crunched}-{ms_unlike.count}.csv', trade_upload_csv)
            ms_positions_og = (pd.read_excel(positions_upload)).to_csv(index=False)
            zip_file.writestr(f'MS Position Download-{ms_unlike.account}.csv', ms_positions_og)

        zip_buffer.seek(0)

        st.download_button(
            label='Download Unlike Package',
            data=zip_buffer,
            file_name=f'{ms_unlike.account}-package-done.zip',
            mime='application/zip'

        )










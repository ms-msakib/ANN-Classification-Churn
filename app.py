import streamlit as st
import tensorflow as tf
import pandas as pd
import pickle

## Page setup
st.set_page_config(page_title='Customer Churn Prediction', page_icon='📉', layout='centered')


## Load the trained model, encoders and scaler (cached so they load only once)
@st.cache_resource
def load_artifacts():
    model = tf.keras.models.load_model('model.h5')

    with open('label_encoder_gender.pkl', 'rb') as file:
        label_encoder_gender = pickle.load(file)

    with open('onehot_encoder_geo.pkl', 'rb') as file:
        onehot_encoder_geo = pickle.load(file)

    with open('scaler.pkl', 'rb') as file:
        scaler = pickle.load(file)

    return model, label_encoder_gender, onehot_encoder_geo, scaler


model, label_encoder_gender, onehot_encoder_geo, scaler = load_artifacts()


## Header
st.title('📉 Customer Churn Prediction')
st.caption('Enter the customer details below to estimate the probability that they will leave the bank.')

## Sidebar
with st.sidebar:
    st.header('About')
    st.write(
        'This app uses an Artificial Neural Network trained on the '
        '**Churn_Modelling** dataset to predict whether a bank customer is likely to churn.'
    )
    threshold = st.slider('Decision threshold', 0.1, 0.9, 0.5, 0.05,
                          help='Customers with a churn probability above this value are flagged as likely to churn.')


## User input
with st.form('customer_form'):
    st.subheader('👤 Personal details')
    col1, col2, col3 = st.columns(3)
    with col1:
        geography = st.selectbox('Geography', onehot_encoder_geo.categories_[0])
    with col2:
        gender = st.selectbox('Gender', label_encoder_gender.classes_)
    with col3:
        age = st.number_input('Age', min_value=18, max_value=92, value=35, step=1)

    st.subheader('🏦 Account details')
    col1, col2 = st.columns(2)
    with col1:
        credit_score = st.number_input('Credit Score', min_value=300, max_value=900, value=650, step=1)
        balance = st.number_input('Balance', min_value=0.0, value=0.0, step=1000.0, format='%.2f')
        estimated_salary = st.number_input('Estimated Salary', min_value=0.0, value=50000.0, step=1000.0, format='%.2f')
    with col2:
        tenure = st.slider('Tenure (years)', 0, 10, 5)
        num_of_products = st.slider('Number of Products', 1, 4, 1)

    col1, col2 = st.columns(2)
    with col1:
        has_cr_card = st.radio('Has Credit Card', ['Yes', 'No'], horizontal=True)
    with col2:
        is_active_member = st.radio('Is Active Member', ['Yes', 'No'], horizontal=True)

    submitted = st.form_submit_button('Predict Churn', type='primary', use_container_width=True)


## Prediction
if submitted:
    # Prepare the input data
    input_data = pd.DataFrame({
        'CreditScore': [credit_score],
        'Gender': [label_encoder_gender.transform([gender])[0]],
        'Age': [age],
        'Tenure': [tenure],
        'Balance': [balance],
        'NumOfProducts': [num_of_products],
        'HasCrCard': [1 if has_cr_card == 'Yes' else 0],
        'IsActiveMember': [1 if is_active_member == 'Yes' else 0],
        'EstimatedSalary': [estimated_salary]
    })

    # One-hot encode 'Geography'
    geo_encoded = onehot_encoder_geo.transform(pd.DataFrame({'Geography': [geography]})).toarray()
    geo_encoded_df = pd.DataFrame(geo_encoded, columns=onehot_encoder_geo.get_feature_names_out(['Geography']))

    # Combine one-hot encoded columns with input data
    input_data = pd.concat([input_data.reset_index(drop=True), geo_encoded_df], axis=1)

    # Scale the input data
    input_data_scaled = scaler.transform(input_data)

    # Predict churn
    prediction = model.predict(input_data_scaled, verbose=0)
    prediction_proba = float(prediction[0][0])

    st.divider()
    st.subheader('📊 Prediction result')

    col1, col2 = st.columns(2)
    col1.metric('Churn Probability', f'{prediction_proba:.1%}')
    col2.metric('Retention Probability', f'{1 - prediction_proba:.1%}')
    st.progress(prediction_proba)

    if prediction_proba > threshold:
        st.error('⚠️ The customer is **likely to churn**. Consider reaching out with a retention offer.')
    else:
        st.success('✅ The customer is **not likely to churn**.')

    with st.expander('View model input'):
        st.dataframe(input_data, hide_index=True)

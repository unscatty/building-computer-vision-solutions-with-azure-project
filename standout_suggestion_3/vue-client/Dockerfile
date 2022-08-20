FROM node:lts-alpine as stage

WORKDIR /app

COPY . /app

RUN export NODE_OPTIONS=--openssl-legacy-provider

RUN npm install

RUN npm run build

WORKDIR /server

ENV VUE_APP_B2C_TENANT "firsttestingb2c"
ENV VUE_APP_B2C_CLIENTID "5aa31939-0254-4dfa-84ad-3048d0a24fe4"
ENV VUE_APP_B2C_SIGNINPOLICY "B2C_1_FE_SIGNUP_SIGNIN"
ENV VUE_APP_B2C_REDIRECT_URI "https://feriaempleoescomipn.com.mx"
ENV VUE_APP_B2C_COMPANY_REGISTER_REDIRECT_URI "https://feriaempleoescomipn.com.mx/empresas/registro"
ENV VUE_APP_B2C_LOGOUT_URI "https://feriaempleoescomipn.com.mx"
ENV VUE_APP_B2C_TOKEN "msal.idtoken"
ENV VUE_APP_B2C_STATE_KEY "msal.state"
ENV VUE_APP_SERVER_HOST "https://feriaempleoescomipn.com.mx/api/v1"

FROM nginx:alpine

COPY --from=stage /app/dist /usr/share/nginx/html
COPY ./nginx-custom.conf /etc/nginx/conf.d/default.conf


import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime
import csv
import logging


class Covid19:
    # args
    def __init__(self):
        self.covid19 = pd.DataFrame()

    @staticmethod
    def test():
        return 'test'

    @staticmethod
    def extract():
        logging.info('extract')

        if os.path.isfile('./input/InformacionComunas.csv'):
            now_ts = datetime.now()
            file_obj = os.stat('./input/InformacionComunas.csv')
            file_ts = datetime.fromtimestamp(file_obj.st_mtime)

            if (now_ts - file_ts).days < 1:
                # Es mayor y ya existen
                return

        # Si no existen o es mayor se descargan
        # print("timestamp now:  {0}\ntimestamp file: {1}".format(now_ts, file_ts))
        urls = [
            'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/input/Otros/InformacionComunas.csv',
            'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto1/Covid-19_std.csv',
            'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto19/CasosActivosPorCom' +
            'una_std.csv',
            'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto38/CasosFallecidosPor' +
            'Comuna_std.csv',
            'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto80/vacunacion_comuna_' +
            '1eraDosis_std.csv',
            'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto80/vacunacion_comuna_' +
            '2daDosis_std.csv',
            'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto80/vacunacion_comuna_' +
            'Refuerzo_std.csv',
            'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto80/vacunacion_comuna_' +
            '4taDosis_std.csv',
            'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto80/vacunacion_comuna_' +
            'UnicaDosis_std.csv'
        ]

        logging.info('downloading...')

        for url in urls:
            r = requests.get(url)  # create HTTP response object
            with open('./input/' + url.rsplit('/', 1)[-1], 'wb') as f:
                f.write(r.content)

    # fin extract

    def transform(self):

        logging.info('transform')

        # comunas
        file = './input/InformacionComunas.csv'

        comunas_df = pd.read_csv(file)

        comunas_df.rename(columns={'Comuna': 'comuna',
                                   'Codigo comuna': 'codigo_comuna',
                                   'Region': 'region',
                                   'Codigo region': 'codigo_region',
                                   'Superficie_km2': 'superficie_km2',
                                   'Poblacion': 'poblacion'
                                   }, inplace=True)

        comunas_df.set_index('codigo_comuna', inplace=True)

        # csv base
        file = './input/Covid-19_std.csv'

        casos_df = pd.read_csv(file)

        # remove rows unknows places
        casos_df = casos_df[casos_df['Codigo comuna'] > -1]

        casos_df.rename(columns={'Codigo comuna': 'codigo_comuna',
                                 'Comuna': 'comuna',
                                 'Casos confirmados': 'casos_confirmados',
                                 'Fecha': 'fecha',
                                 'Poblacion': 'poblacion',
                                 'Codigo region': 'codigo_region',
                                 'Region': 'region'}, inplace=True)

        casos_df.set_index(['codigo_comuna', 'fecha'])

        # dates group by
        fechas_df = casos_df.groupby("fecha", sort=False)["fecha"].count()

        fechas_df = dict(fechas_df)

        covid19_column_names = ["region",
                                "codigo_region",
                                "superficie_km2",
                                "poblacion",
                                "fecha",
                                "codigo_comuna",
                                "comuna",
                                "casos_confirmados",
                                "casos_diarios"]

        covid19_df = pd.DataFrame(columns=covid19_column_names)

        covid19_df.set_index(['codigo_comuna', 'fecha'])

        temp_df = ''

        # loop range dates (230 aprox dias)
        # loop para validar casos-comunas y obtener numero de casos diarios
        for fecha in fechas_df:

            # print(fecha)
            aux_df = casos_df[casos_df['fecha'] == fecha]

            # se copia el daframe de comunas inicializado antes del bucle
            comunas_copy_df = comunas_df

            # merge: aqui se une todo y si faltan comunas en el casos_df se rellenan por ser left join
            # la intencion de esto es por si faltan comunas en casos_df
            comunas_copy_df = pd.merge(
                comunas_copy_df,
                aux_df,
                on='codigo_comuna',
                how='left',
                suffixes=('', '_drop')
                )
            comunas_copy_df.drop([col for col in covid19_df.columns if 'drop' in col], axis=1, inplace=True)

            # return

            # debido que el archivo esta incremental se dese restar el día anterio con casos_confirmados
            # hay casos en que da negativo, se supone por ajuste de datos
            # print("casos_diarios...")
            if isinstance(temp_df, pd.DataFrame):
                comunas_copy_df['casos_diarios'] = comunas_copy_df['casos_confirmados'] - \
                    temp_df['casos_confirmados']
            else:
                comunas_copy_df['casos_diarios'] = comunas_copy_df['casos_confirmados']

            # casos_diarios negativo dejar en 0?

            temp_df = comunas_copy_df

            # add comunas_copy_df to covid19
            # print("append...")
            # covid19_df = covid19_df.append(comunas_copy_df)
            # pd.concat([df, new_df], axis=0, ignore_index=True)
            covid19_df = pd.concat([covid19_df, comunas_copy_df], axis=0, ignore_index=True)

            # if fecha == "2021-07-02":
            #    break
        # fin loop dates

        # print(covid19_df.head(10))
        # return

        # init --- CasosActivosPorComuna ---
        # archivo ya viene con mismas fechas
        file = './input/CasosActivosPorComuna_std.csv'

        casos_activos_df = pd.read_csv(file)

        # remove rows unknows places
        casos_activos_df = casos_activos_df[casos_activos_df['Codigo comuna'] > -1]

        # rename campos
        casos_activos_df.rename(columns={'Codigo comuna': 'codigo_comuna',
                                         'Comuna': 'comuna',
                                         'Casos activos': 'casos_activos',
                                         'Fecha': 'fecha',
                                         'Poblacion': 'poblacion',
                                         'Codigo region': 'codigo_region',
                                         'Region': 'region'}, inplace=True)

        casos_activos_df.set_index(['codigo_comuna', 'fecha'])

        covid19_df = pd.merge(
            covid19_df, casos_activos_df, on=[
                'codigo_comuna', 'fecha'], how='left', suffixes=(
                '', '_drop'))
        covid19_df.drop(
            [col for col in covid19_df.columns if 'drop' in col], axis=1, inplace=True)

        # init --- FallecidosPorComuna ---
        # archivo ya viene con mismas fechas
        file = './input/CasosFallecidosPorComuna_std.csv'

        fallecidos_df = pd.read_csv(file)

        # remove rows unknows places
        fallecidos_df = fallecidos_df[fallecidos_df['Codigo comuna'] > -1]

        # rename campos
        fallecidos_df.rename(columns={'Codigo comuna': 'codigo_comuna',
                                      'Comuna': 'comuna',
                                      'Casos fallecidos': 'casos_fallecidos',
                                      'Fecha': 'fecha',
                                      'Poblacion': 'poblacion',
                                      'Codigo region': 'codigo_region',
                                      'Region': 'region'}, inplace=True)

        fallecidos_df.set_index(['codigo_comuna', 'fecha'])

        covid19_df = pd.merge(
            covid19_df, fallecidos_df, on=[
                'codigo_comuna', 'fecha'], how='left', suffixes=(
                '', '_drop'))
        covid19_df.drop(
            [col for col in covid19_df.columns if 'drop' in col], axis=1, inplace=True)

        # init --- PrimeraDosis ---
        vacunacion_tmp = self.vacunacion(
            fechas_df,
            './input/vacunacion_comuna_1eraDosis_std.csv',
            'Primera Dosis',
            'primera_dosis')

        # merge covid19_df casos_activos_df
        covid19_df = pd.merge(
            covid19_df, vacunacion_tmp, on=[
                'codigo_comuna', 'fecha'], how='left', suffixes=(
                '', '_drop'))
        covid19_df.drop(
            [col for col in covid19_df.columns if 'drop' in col], axis=1, inplace=True)

        # init --- SegundaDosis ---
        vacunacion_tmp = self.vacunacion(
            fechas_df,
            './input/vacunacion_comuna_2daDosis_std.csv',
            'Segunda Dosis',
            'segunda_dosis')

        # merge covid19_df casos_activos_df
        covid19_df = pd.merge(
            covid19_df, vacunacion_tmp, on=[
                'codigo_comuna', 'fecha'], how='left', suffixes=(
                '', '_drop'))
        covid19_df.drop(
            [col for col in covid19_df.columns if 'drop' in col], axis=1, inplace=True)

        # init --- Dosis refuerzo ---
        vacunacion_tmp = self.vacunacion(
            fechas_df,
            './input/vacunacion_comuna_Refuerzo_std.csv',
            'Dosis Refuerzo',
            'dosis_refuerzo')

        # merge covid19_df casos_activos_df
        covid19_df = pd.merge(
            covid19_df, vacunacion_tmp, on=[
                'codigo_comuna', 'fecha'], how='left', suffixes=(
                '', '_drop'))
        covid19_df.drop(
            [col for col in covid19_df.columns if 'drop' in col], axis=1, inplace=True)

        # init --- CuartaDosis ---
        vacunacion_tmp = self.vacunacion(
            fechas_df,
            './input/vacunacion_comuna_4taDosis_std.csv',
            'Cuarta Dosis',
            'cuarta_dosis')

        # merge covid19_df casos_activos_df
        covid19_df = pd.merge(covid19_df, vacunacion_tmp, on=['codigo_comuna', 'fecha'], how='left',
                              suffixes=('', '_drop'))
        covid19_df.drop([col for col in covid19_df.columns if 'drop' in col], axis=1, inplace=True)

        # init --- DosisUnica ---
        vacunacion_tmp = self.vacunacion(
            fechas_df,
            './input/vacunacion_comuna_UnicaDosis_std.csv',
            'Unica Dosis',
            'unica_dosis')

        # merge covid19_df casos_activos_df
        covid19_df = pd.merge(covid19_df, vacunacion_tmp, on=['codigo_comuna', 'fecha'], how='left',
                              suffixes=('', '_drop'))
        covid19_df.drop([col for col in covid19_df.columns if 'drop' in col], axis=1, inplace=True)

        # comuna - paso a paso later
        covid19_df = covid19_df.replace(np.nan, 0)

        self.covid19 = covid19_df

        # https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/input/UC/Positividad%20por%20comuna.csv

        return

    def load(self):
        logging.info('load')
        covid19_df = self.covid19
        covid19_df.head(10)
        covid19_df.info(memory_usage="deep")
        covid19_df.to_csv('./output/covid19.csv')
        covid19_df.to_json(r'./output/covid19.json', orient='records')

        file = open('./output/covid19.csv')
        csv_rows = len(file.readlines())

        openfile = open('./output/covid19.csv', 'r')
        csvfile = csv.reader(openfile)

        header = next(csvfile)

        header[0] = "id"

        headers = map((lambda x: '`' + x + '`'), header)

        f = open("./output/covid19.sql", "w")

        tabla = "DROP TABLE IF EXISTS casos;\nCREATE TABLE casos(\n" \
                "id                INTEGER  NOT NULL PRIMARY KEY,\n" \
                "region            VARCHAR(41) NOT NULL,\n" \
                "codigo_region     INTEGER  NOT NULL,\n" \
                "superficie_km2    NUMERIC(9,2) NOT NULL,\n" \
                "poblacion         NUMERIC(8,1) NOT NULL,\n" \
                "fecha             DATE  NOT NULL,\n" \
                "codigo_comuna     INTEGER  NOT NULL,\n" \
                "comuna            VARCHAR(20) NOT NULL,\n" \
                "casos_confirmados NUMERIC(8,1) NOT NULL,\n" \
                "casos_diarios     NUMERIC(6,1) NOT NULL,\n" \
                "casos_activos     NUMERIC(6,1) NOT NULL,\n" \
                "casos_fallecidos  NUMERIC(6,1) NOT NULL,\n" \
                "primera_dosis     NUMERIC(7,1) NOT NULL,\n" \
                "segunda_dosis     NUMERIC(7,1) NOT NULL,\n" \
                "dosis_refuerzo    NUMERIC(7,1) NOT NULL,\n" \
                "cuarta_dosis      NUMERIC(6,1) NOT NULL,\n" \
                "unica_dosis       NUMERIC(6,1) NOT NULL\n" \
                ");\n"

        f.write(tabla)

        insert = '\nINSERT INTO casos (' + ", ".join(headers) + ") VALUES \n"

        lineas = 0
        contador = 1

        for row in csvfile:

            if lineas == 0:
                value = insert
            else:
                value = ""

            value += " (" + row[0] + "," \
                                     "'" + row[1].replace("'", " ") + "'," \
                     + row[2] + "," \
                     + row[3] + "," \
                     + row[4] + "," \
                                "'" + row[5] + "'," \
                     + row[6] + "," \
                                "'" + row[7].replace("'", " ") + "'," \
                     + row[8] + "," \
                     + row[9] + "," \
                     + row[10] + "," \
                     + row[11] + "," \
                     + row[12] + "," \
                     + row[13] + "," \
                     + row[14] + "," \
                     + row[15] + "," \
                     + row[16] + ")"

            if lineas == 1000 or contador + 1 == csv_rows:
                value += ";"
                lineas = 0
            else:
                value += ","
                lineas = lineas + 1

            contador = contador + 1
            f.write(value)

        openfile.close()
    
    @staticmethod
    def vacunacion(fechas_df, file, columna_glosa, columna_nombre):

        vacunacion_tmp_column_names = ["region", "fecha", "codigo_comuna", columna_nombre]

        vacunacion_tmp = pd.DataFrame(columns=vacunacion_tmp_column_names)

        vacunacion_df = pd.read_csv(file)

        # remove rows unknows places
        vacunacion_df = vacunacion_df[vacunacion_df[columna_glosa] > -1]

        # rename campos
        vacunacion_df.rename(columns={'Codigo comuna': 'codigo_comuna', 'Comuna': 'comuna', 'Fecha': 'fecha',
                                      columna_glosa: columna_nombre}, inplace=True)

        vacunacion_df.set_index(['codigo_comuna', 'fecha'])

        vacunacion_df['fecha'] = pd.to_datetime(
            vacunacion_df['fecha'], errors='coerce').dt.date

        # Get first value from dictionary
        fecha_anterior = ""

        # casos activos comuna loop fechas_df
        for fecha in fechas_df:

            # print(fecha)

            fecha_anterior = fecha_anterior == "" and fecha or fecha_anterior

            # query cast fecha para between y sum

            # _fecha > fecha[-1] && fecha < fecha
            # mini datafrae del dia

            startdate = pd.to_datetime(fecha_anterior).date()
            enddate = pd.to_datetime(fecha).date()

            aux_df = vacunacion_df[(vacunacion_df['fecha'] > startdate) & (vacunacion_df['fecha'] <= enddate)]\
                .groupby('codigo_comuna')[columna_nombre].sum().reset_index()

            aux_df['fecha'] = fecha

            fecha_anterior = fecha

            # print("append...")
            # /covid19etl/./covid19.py:426: FutureWarning: The frame.append method is deprecated and will be
            # removed from pandas in a future version. Use pandas.concat instead.

            # vacunacion_tmp = vacunacion_tmp.append(aux_df)
            vacunacion_tmp = pd.concat([vacunacion_tmp, aux_df], axis=0, ignore_index=True)

            # if fecha == "2021-01-08":
            # return
        return vacunacion_tmp

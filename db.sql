CREATE DATABASE VideoRecognitionDB;
USE VideoRecognitionDB;

CREATE TABLE sis_m_video(
    ncodigo SERIAL NOT NULL,
    cnombre varchar(255),
    clinkbucket varchar(255),
    netq0 float ,
    netq1 float ,
    netq2 float ,
    netq3 float ,
    netq4 float ,
    netq5 float ,
    netq6 float ,
    netq7 float ,
    netq8 float ,
    netq9 float ,
    netq10 float ,
    netq11 float ,
    netq12 float ,
    netq13 float ,
    netq14 float ,
    netq15 float ,
    netq16 float ,
    netq17 float ,
    netq18 float ,
    netq19 float ,
    netq20 float ,
    PRIMARY KEY (ncodigo)
);

/*delete  from sis_m_video*/
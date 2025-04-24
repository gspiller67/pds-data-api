--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4 (Debian 17.4-1.pgdg120+2)
-- Dumped by pg_dump version 17.4 (Debian 17.4-1.pgdg120+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: CONNECTIONOPTIONS; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."CONNECTIONOPTIONS" (
    id uuid NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public."CONNECTIONOPTIONS" OWNER TO postgres;

--
-- Name: CONNECTIONS; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."CONNECTIONS" (
    id uuid NOT NULL,
    connection_name character varying NOT NULL,
    connection_description character varying,
    connection_config bytea NOT NULL,
    connection_type_id uuid NOT NULL,
    direction boolean NOT NULL
);


ALTER TABLE public."CONNECTIONS" OWNER TO postgres;

--
-- Name: PDSTABLES; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."PDSTABLES" (
    id uuid NOT NULL,
    config_name character varying NOT NULL,
    source_connection_id uuid NOT NULL,
    destination_connection_id uuid NOT NULL,
    table_name character varying NOT NULL,
    active boolean
);


ALTER TABLE public."PDSTABLES" OWNER TO postgres;

--
-- Name: TABLECOLLUMNS; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."TABLECOLLUMNS" (
    id uuid NOT NULL,
    pds_table_id uuid NOT NULL,
    column_name character varying NOT NULL,
    data_type character varying NOT NULL,
    active boolean
);


ALTER TABLE public."TABLECOLLUMNS" OWNER TO postgres;

--
-- Data for Name: CONNECTIONOPTIONS; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."CONNECTIONOPTIONS" (id, name) FROM stdin;
54a5b201-24cf-45d5-98f8-1a4dc7cde163	pds
51592cfb-4bb1-4a71-a33b-a11e02e4da79	postgresql
\.


--
-- Data for Name: CONNECTIONS; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."CONNECTIONS" (id, connection_name, connection_description, connection_config, connection_type_id, direction) FROM stdin;
f251e484-c252-484d-afbd-a1d0de8a37c4	Unifier Sales Data	pds connection	\\x7b0d0a202020202275726c223a202268747470733a2f2f7573312e756e696669657273616c65732e6f7261636c65636c6f75642e636f6d222c0d0a2020202022757365726e616d65223a2022796f75725f757365726e616d65222c0d0a202020202270617373776f7264223a2022796f75725f70617373776f7264220d0a7d	54a5b201-24cf-45d5-98f8-1a4dc7cde163	t
024b2ad6-628a-4bcf-92a0-f7e47febb64c	Postgres DB	postgresql connection	\\x7b0d0a2020202022686f7374223a20226c6f63616c686f7374222c0d0a2020202022706f7274223a20353433322c0d0a20202020226461746162617365223a2022796f75725f64617461626173655f6e616d65222c0d0a2020202022757365726e616d65223a2022706f737467726573222c0d0a202020202270617373776f7264223a2022706f737467726573220d0a7d	51592cfb-4bb1-4a71-a33b-a11e02e4da79	f
\.


--
-- Data for Name: PDSTABLES; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."PDSTABLES" (id, config_name, source_connection_id, destination_connection_id, table_name, active) FROM stdin;
f05da93e-4d7f-40e9-ac21-4e61e86f4556	UNIFIER_UXFINV	f251e484-c252-484d-afbd-a1d0de8a37c4	024b2ad6-628a-4bcf-92a0-f7e47febb64c	UNIFIER_UXFINV	t
\.


--
-- Data for Name: TABLECOLLUMNS; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."TABLECOLLUMNS" (id, pds_table_id, column_name, data_type, active) FROM stdin;
318de33e-1d8c-45dc-90e2-2a9822d4f2d9	f05da93e-4d7f-40e9-ac21-4e61e86f4556	ID	INTEGER	t
4acbb778-c37e-4f26-90b5-30613d6cc558	f05da93e-4d7f-40e9-ac21-4e61e86f4556	RECORD_NO	VARCHAR	t
67ff0555-1199-4d0c-8bdb-c56a99259151	f05da93e-4d7f-40e9-ac21-4e61e86f4556	TITLE	VARCHAR	t
c6c042d1-2149-401d-ac8b-a0051b057db4	f05da93e-4d7f-40e9-ac21-4e61e86f4556	DUE_DATE	DATE	t
10215d7e-bfcf-49d0-a8aa-cd854c15d50f	f05da93e-4d7f-40e9-ac21-4e61e86f4556	END_DATE	DATE	t
4f05fb7c-2e69-4f03-b09d-0c811d95963e	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UUU_RECORD_LAST_UPDATE_DATE	DATE	t
fda368d5-0165-437a-b831-c69374493817	f05da93e-4d7f-40e9-ac21-4e61e86f4556	PROCESS_STATUS	INTEGER	t
aee12e38-9b80-43d9-9db1-55f8839aa880	f05da93e-4d7f-40e9-ac21-4e61e86f4556	STATUS	VARCHAR	t
ca94e9fb-44ca-4bf2-9c0d-87bfb35dadce	f05da93e-4d7f-40e9-ac21-4e61e86f4556	CREATOR_ID	INTEGER	t
c627575d-f7c8-4fd2-bec0-27e70b4cb536	f05da93e-4d7f-40e9-ac21-4e61e86f4556	PROJECT_ID	INTEGER	t
6c3d2c27-7ba3-4acd-9937-56b7c2b80f58	f05da93e-4d7f-40e9-ac21-4e61e86f4556	ATTACH_CNT	INTEGER	t
297c49c1-0e35-4d38-ae7a-8d0cab3be936	f05da93e-4d7f-40e9-ac21-4e61e86f4556	REASON	INTEGER	t
f8d3f398-6eb5-4705-b242-509b6e0d9db2	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UVEFAXTB16	VARCHAR	t
0894db22-13d5-41e5-9bbb-143d0963c7eb	f05da93e-4d7f-40e9-ac21-4e61e86f4556	GEN_POREFERENCE_TB	VARCHAR	t
7b70ab44-4309-45e5-b25f-6c42f1c17b5a	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENLINEITEMCOUNTDA	INTEGER	t
3e9ddb3c-80fd-45d1-8608-ffe346d14e22	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UVEPRIMARYCONTACTTB64	VARCHAR	t
a558b2b6-d336-4475-88fb-569d58960061	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UPOPONUMBERTXT16	VARCHAR	t
c7c04b18-0cf8-4915-81e9-0972bcfc9497	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UPAINVOICEDATEDOP	DATE	t
f53bae7e-cffb-4d99-b805-2ff49c2d8ec7	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENACTIVITYDPK	INTEGER	t
7d3c8ef7-e63c-42e6-af95-68ce216ce356	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UINVPOTITLE	VARCHAR	t
cd80d105-e19c-447b-a0b6-29b877f92dfe	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENCITYTXT50	VARCHAR	t
2f632778-918d-4d9d-9216-7408dc66566c	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UUU_DM_PUBLISH_PATH	VARCHAR	t
d8f61c1a-6df3-470f-9e19-7f353d084678	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENZIPCODETXT16	VARCHAR	t
52f2734e-7f44-40b9-ac63-1f7043013470	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENP6PLANNEDFINISHDOP	DATE	t
61e5e42c-e010-4167-8eac-86744e71c742	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UVEEMAILTB120	VARCHAR	t
61a6828e-1f76-4bb4-b803-b17b0a5504e4	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENADDRESS3TXT120	VARCHAR	t
fb18130e-cdd5-447b-b048-286afbbde43f	f05da93e-4d7f-40e9-ac21-4e61e86f4556	AMOUNT	INTEGER	t
c9b31486-18a2-4bde-97b1-0e947900cb31	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UUU_CREATION_DATE	DATE	t
9c17e2e1-98dc-4b99-842b-59dc837e0d4d	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENP6PLANNEDCOSTCA	INTEGER	t
99264876-5038-48ab-aae8-0e2312b9e539	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UVEPHONETB64	VARCHAR	t
ccee1eea-5ec0-4476-935d-6fee4f7b50ce	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UPACHECKPROCDATEDOP	DATE	t
b19de57c-023e-402f-8724-45db90e9fcf1	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UINVPODATEDP	DATE	t
9dd6fc86-9063-4822-9d6e-007b438d7f64	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UVEVENDORNAMETB50	VARCHAR	t
75e9d0c2-9327-405d-91be-00013123596e	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENADDRESS1TXT120	VARCHAR	t
a3106568-8e4a-4aaf-a879-58c2cb3a4b14	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UPACHECKNOTB50	VARCHAR	t
3fc71e28-c018-411a-bc8b-f8e98f9eb590	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENP6PLANNEDSTARTDOP	DATE	t
274609fa-b3f5-48e2-b661-58e7841375df	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UUU_EFFECTIVE_DATE	DATE	t
3c06b7d6-0180-48ed-97ed-7fc2dc2d1c23	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENADDRESS2TXT120	VARCHAR	t
844af413-c0aa-452b-ab5f-2168714c6180	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENCOUNTRYPD	VARCHAR	t
6e36ce0f-d264-448c-8bdf-a8845b6f399e	f05da93e-4d7f-40e9-ac21-4e61e86f4556	CURRENCYID	INTEGER	t
aae98ccb-8b10-49b8-99cb-3c4dca972fdf	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UVEVENDORIDTB16	VARCHAR	t
0574c77f-76e9-41a0-9a52-714134d4a99a	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UPACHECKDATEDOP	DATE	t
3792894a-af78-46de-a275-ed7860eecbe5	f05da93e-4d7f-40e9-ac21-4e61e86f4556	UGENSTATEPD	VARCHAR	t
\.


--
-- Name: CONNECTIONOPTIONS CONNECTIONOPTIONS_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CONNECTIONOPTIONS"
    ADD CONSTRAINT "CONNECTIONOPTIONS_name_key" UNIQUE (name);


--
-- Name: CONNECTIONOPTIONS CONNECTIONOPTIONS_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CONNECTIONOPTIONS"
    ADD CONSTRAINT "CONNECTIONOPTIONS_pkey" PRIMARY KEY (id);


--
-- Name: CONNECTIONS CONNECTIONS_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CONNECTIONS"
    ADD CONSTRAINT "CONNECTIONS_pkey" PRIMARY KEY (id);


--
-- Name: PDSTABLES PDSTABLES_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."PDSTABLES"
    ADD CONSTRAINT "PDSTABLES_pkey" PRIMARY KEY (id);


--
-- Name: TABLECOLLUMNS TABLECOLLUMNS_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TABLECOLLUMNS"
    ADD CONSTRAINT "TABLECOLLUMNS_pkey" PRIMARY KEY (id);


--
-- Name: CONNECTIONS CONNECTIONS_connection_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CONNECTIONS"
    ADD CONSTRAINT "CONNECTIONS_connection_type_id_fkey" FOREIGN KEY (connection_type_id) REFERENCES public."CONNECTIONOPTIONS"(id);


--
-- Name: PDSTABLES PDSTABLES_destination_connection_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."PDSTABLES"
    ADD CONSTRAINT "PDSTABLES_destination_connection_id_fkey" FOREIGN KEY (destination_connection_id) REFERENCES public."CONNECTIONS"(id);


--
-- Name: PDSTABLES PDSTABLES_source_connection_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."PDSTABLES"
    ADD CONSTRAINT "PDSTABLES_source_connection_id_fkey" FOREIGN KEY (source_connection_id) REFERENCES public."CONNECTIONS"(id);


--
-- Name: TABLECOLLUMNS TABLECOLLUMNS_pds_table_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TABLECOLLUMNS"
    ADD CONSTRAINT "TABLECOLLUMNS_pds_table_id_fkey" FOREIGN KEY (pds_table_id) REFERENCES public."PDSTABLES"(id);


--
-- PostgreSQL database dump complete
--


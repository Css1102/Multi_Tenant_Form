--
-- PostgreSQL database dump
--

\restrict avl2XMLcPPk2e45YzoELIGsbIOLVVQ0w18aLoMbtg63fkzC0dATYnWzT1mqLhj6

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: fileattachment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fileattachment (
    id uuid NOT NULL,
    submission_id uuid NOT NULL,
    storage_path character varying NOT NULL,
    original_filename character varying NOT NULL,
    mime_type character varying NOT NULL,
    size_bytes integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    field_id character varying
);


--
-- Name: form; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.form (
    id uuid NOT NULL,
    title character varying NOT NULL,
    organization_id uuid NOT NULL,
    is_active boolean NOT NULL,
    structure jsonb,
    created_at timestamp without time zone NOT NULL,
    created_by_user_id uuid
);


--
-- Name: formsubmission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.formsubmission (
    id uuid NOT NULL,
    form_id uuid NOT NULL,
    answers jsonb,
    created_at timestamp without time zone NOT NULL,
    submitted_by_user_id uuid
);


--
-- Name: organization; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.organization (
    id uuid NOT NULL,
    name character varying NOT NULL
);


--
-- Name: organizationinvite; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.organizationinvite (
    id uuid NOT NULL,
    organization_id uuid NOT NULL,
    role character varying NOT NULL,
    used_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."user" (
    id uuid NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    organization_id uuid NOT NULL,
    role character varying DEFAULT 'member'::character varying NOT NULL
);


--
-- Data for Name: fileattachment; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fileattachment (id, submission_id, storage_path, original_filename, mime_type, size_bytes, created_at, field_id) FROM stdin;
567f5caa-bee8-4424-928b-bcf62f1a3c97	2d95d65f-72dc-46bb-baf2-c3fba51efe64	secure_storage_vault/76597306211b488a8d784e65a9bbedee_resume.pdf	resume.pdf	application/pdf	29	2026-07-26 11:45:18.993181	\N
1cffdea2-d4e2-4672-a8ad-ec706bae5b96	e47aa713-f22d-4cf4-a1b1-a5538aa360c4	secure_storage_vault/569b81a9f99843e8b4867b660e5366cf_magoosh-gre-1000-words_oct01.pdf	magoosh-gre-1000-words_oct01.pdf	application/pdf	908434	2026-08-22 11:49:15.752033	\N
45566f8f-6fa6-4cc0-a8c6-3501ed146eaf	cd20c462-d6e2-4df2-85f5-a7d5722d34f2	secure_storage_vault/6066b6b2df8747d19cc848f0d6f566f3_magoosh-gre-1000-words_oct01.pdf	magoosh-gre-1000-words_oct01.pdf	application/pdf	908434	2026-08-23 08:10:34.955469	\N
3052d142-c795-4a4b-9764-a37c2a100226	298b451d-ac01-40cd-811e-abc4deb0a916	secure_storage_vault/10fae5b4564d44bb83f90b9f93fb419f_Chiranjeev_Resume_switch (8).pdf	Chiranjeev_Resume_switch (8).pdf	application/pdf	229492	2026-08-23 08:52:30.465952	\N
cf7b8172-abef-4e93-9ed3-02245ec4c11f	f07b741d-3554-4799-b02c-950247523d4a	secure_storage_vault/ed7763a718f4436da77bfbe4bda1981f_Chiranjeev_Resume_switch (10) (1).pdf	Chiranjeev_Resume_switch (10) (1).pdf	application/pdf	229480	2026-08-23 08:54:29.352248	\N
3de98aa1-f818-4d80-9911-e20b1f5dc69d	a51b2e4f-ed42-4de8-8542-cc9a85bb2c1b	secure_storage_vault/d5486c2fe7b045b9bb3ed5c5bac408d3_BLR_GOX_26062026_27134258668.pdf	BLR_GOX_26062026_27134258668.pdf	application/pdf	72095	2026-08-30 12:32:49.022335	field_fe5797fb
\.


--
-- Data for Name: form; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.form (id, title, organization_id, is_active, structure, created_at, created_by_user_id) FROM stdin;
aaf4be30-4ebc-498a-9752-494405f3b6df	my_form_1	c6439e66-bd32-4bf0-ac86-9281239463f8	t	[]	2026-08-09 08:44:38.561559	\N
bb287ec6-c6b2-4724-85ec-de3782011735	my_form_2	c6439e66-bd32-4bf0-ac86-9281239463f8	t	[]	2026-08-09 08:56:33.386484	\N
4a204778-b280-4253-a1ce-75d79d35421d	form_3_tcs	c6439e66-bd32-4bf0-ac86-9281239463f8	t	[]	2026-08-15 10:19:43.041693	\N
c9e4e894-ed75-453f-b073-6f906fc3269e	form_4_org	c6439e66-bd32-4bf0-ac86-9281239463f8	t	[]	2026-08-16 17:19:06.193066	\N
eb106bea-c177-419b-a660-1512c2501b1f	form_org_tcs	c6439e66-bd32-4bf0-ac86-9281239463f8	t	[{"id": "field_e070ec08", "type": "text", "label": "Name", "validation": {"required": true}}, {"id": "field_a012efdd", "type": "number", "label": "Age", "validation": {"required": true}}, {"id": "field_a4b295ab", "type": "number", "label": "Year of Passout", "validation": {"required": true}}, {"id": "field_6031041c", "type": "email", "label": "Mail Id", "validation": {"required": true}}, {"id": "field_742064c9", "type": "file", "label": "Latest Resume", "validation": {"required": true}}, {"id": "field_81b63606", "type": "text", "label": "Father's name", "validation": {"required": false}}, {"id": "field_d2c89978", "type": "number", "label": "CGPA", "validation": {"required": true}}]	2026-08-16 18:44:01.058104	\N
7bd48e2f-0f1e-4f81-9d08-f72088d6b345	Assistant Recruitment	03854879-49d0-49fc-ada4-3b037c11bb48	t	[{"id": "field_79735ce7", "type": "text", "label": "Full Name", "validation": {"required": true}}, {"id": "field_79923580", "type": "number", "label": "Age", "validation": {"required": true}}, {"id": "field_ae8458f4", "type": "text", "label": "Place of residence", "validation": {"required": true}}, {"id": "field_f50a7fd0", "type": "text", "label": "Highest Qualification", "validation": {"required": true}}, {"id": "field_63dc85c4", "type": "file", "label": "Resume", "validation": {"required": true}}]	2026-08-22 11:17:44.439413	\N
8d6f404b-bb3d-40fa-a259-46e904e6e360	Software Engineer Interview Feedback	d88b63c4-48ba-4651-bfb9-f63a34f3605c	t	[{"id": "candidate_name", "type": "text", "label": "Candidate Name", "validation": {"required": true, "min_length": 2}}, {"id": "code_quality", "type": "number", "label": "Code Quality Score (1-10)", "validation": {"required": true}}]	2026-07-26 11:30:53.429346	91bc5811-da95-44cf-ab99-874fa91b94b7
b65daad5-cb39-4ae1-9acd-ab914baf50cc	Software Engineer Interview Feedback	d88b63c4-48ba-4651-bfb9-f63a34f3605c	t	[{"id": "candidate_name", "type": "text", "label": "Candidate Name", "validation": {"required": true, "min_length": 2}}, {"id": "code_quality", "type": "number", "label": "Code Quality Score (1-10)", "validation": {"required": true}}]	2026-07-26 11:35:18.585393	91bc5811-da95-44cf-ab99-874fa91b94b7
a1d423a1-ed5e-4a98-9607-d6a46890ef09	Software Engineer Interview Feedback	d88b63c4-48ba-4651-bfb9-f63a34f3605c	t	[{"id": "candidate_name", "type": "text", "label": "Candidate Name", "validation": {"required": true, "min_length": 2}}, {"id": "code_quality", "type": "number", "label": "Code Quality Score (1-10)", "validation": {"required": true}}]	2026-07-26 11:42:55.251247	91bc5811-da95-44cf-ab99-874fa91b94b7
b5e07219-0839-438e-9dac-94ecd9a341d2	Software Engineer Interview Feedback	d88b63c4-48ba-4651-bfb9-f63a34f3605c	t	[{"id": "candidate_name", "type": "text", "label": "Candidate Name", "validation": {"required": true, "min_length": 2}}, {"id": "code_quality", "type": "number", "label": "Code Quality Score (1-10)", "validation": {"required": true}}]	2026-07-26 11:45:18.974243	91bc5811-da95-44cf-ab99-874fa91b94b7
dad3c27a-8f1a-4727-a238-737640635f7b	Onboarding Form	40dc9450-afe9-4bca-87ce-5a7c4cd93aae	t	[{"id": "field_92632ecd", "type": "text", "label": "Full Name", "validation": {"required": true}}, {"id": "field_b37c5980", "type": "number", "label": "Age", "validation": {"required": true}}, {"id": "field_6eb43d48", "type": "file", "label": "Resume/Cover Letter", "validation": {"required": true}}, {"id": "field_b2c49d2e", "type": "text", "label": "Date of Joining", "validation": {"required": true}}, {"id": "field_ad72fc94", "type": "text", "label": "Notice Period(in months)", "validation": {"required": true}}]	2026-08-22 13:40:02.661605	48e1b310-a296-4275-b5a5-b2b7bd9cb981
e695051f-4b36-4173-839e-0de2e894b725	Offsite Data Collection	8112cdf3-0d50-4f1a-89b9-f925a7ff355c	t	[{"id": "field_ed6e57a1", "type": "text", "label": "Full Name", "validation": {"required": true}}, {"id": "field_1d8327b6", "type": "number", "label": "Employee Id", "validation": {"required": true}}, {"id": "field_50f9c2b9", "type": "yes_no", "label": "Willing to pay 1500 for one day offsite at resort", "validation": {"required": true}}, {"id": "field_5a16a08c", "type": "file", "label": "Payment screenshot as pdf.", "validation": {"required": true}}]	2026-08-23 12:22:38.246992	0df0cb9f-1e4a-41f0-8ad5-c9d8627e012e
6196b179-76f2-4ea2-a64e-9cdce60e178a	Mandatory Course Completion	2314f35e-f9f0-4304-a19c-0766b6f9a197	t	[{"id": "field_8ef976a7", "type": "text", "label": "Full Name", "validation": {"required": true}}, {"id": "field_bccd6727", "type": "number", "label": "Employee Id", "validation": {"required": true}}, {"id": "field_ea5f2f39", "type": "yes_no", "label": "Have you completed the Maqndatory Courses?", "validation": {"required": true}}, {"id": "field_fe5797fb", "type": "file", "label": "Attach Proof of Completion", "validation": {"required": true}}]	2026-08-30 10:55:47.96365	85a13a7d-9d35-43b5-8b19-89e7b64e75f0
\.


--
-- Data for Name: formsubmission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.formsubmission (id, form_id, answers, created_at, submitted_by_user_id) FROM stdin;
2d95d65f-72dc-46bb-baf2-c3fba51efe64	b5e07219-0839-438e-9dac-94ecd9a341d2	{"code_quality": 9, "candidate_name": "Jane Doe"}	2026-07-26 11:45:18.985668	\N
083e929d-8214-4cde-af06-9f5ba35f2761	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-15 10:06:02.144618	\N
bc2e3bdc-576f-4905-9756-8241f28133fd	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-15 10:14:54.862272	\N
ed407c37-f167-4d9e-9738-8e9883d0299a	bb287ec6-c6b2-4724-85ec-de3782011735	{}	2026-08-15 10:15:07.994878	\N
692be09f-d5e7-4117-a131-8a4cc918eb02	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-15 10:19:49.03068	\N
9efb82d3-a974-481d-b9fc-b7d413f6f9bc	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-15 10:27:22.336483	\N
c5fb0d46-28e9-4d9f-81ad-cdcd190fea03	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-15 10:27:33.600414	\N
8ef2f8c0-eae3-460d-a386-006418b63f00	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-15 10:27:38.532966	\N
c7686d2a-5dda-4f4c-90ae-340bb9fb0ac9	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-15 10:28:58.635401	\N
297f829c-f1c3-4cdd-abc0-57548e1ecf79	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-15 17:58:35.504266	\N
fbe819a7-a807-458e-83bb-0701573015bc	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-15 18:09:06.555929	\N
6e4ed7fd-544e-48b6-97fd-7204d1c3924c	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-15 18:11:18.283451	\N
2c579d59-0bd8-40d8-b811-29dab51db342	bb287ec6-c6b2-4724-85ec-de3782011735	{}	2026-08-15 18:14:08.642499	\N
3d25c604-c5eb-498b-aa9e-55cc0eff9673	bb287ec6-c6b2-4724-85ec-de3782011735	{}	2026-08-15 18:15:01.944225	\N
a0dbccc9-dbb5-41fd-88bb-f15c4efcb589	bb287ec6-c6b2-4724-85ec-de3782011735	{}	2026-08-16 16:55:21.787186	\N
54dc69e9-eb1a-44e2-a4d9-55ea68e88ff7	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-16 16:59:46.081286	\N
52792438-d77a-4c4c-b629-d91f74f1386f	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-16 17:08:03.86931	\N
e5f8206c-c632-43c1-9a16-61cd05805252	bb287ec6-c6b2-4724-85ec-de3782011735	{}	2026-08-16 17:08:08.941717	\N
9c3dc3f7-520d-46c4-ad91-50800282c7bb	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-16 18:41:58.215924	\N
e59439f3-342d-4956-8645-395e873659ba	c9e4e894-ed75-453f-b073-6f906fc3269e	{}	2026-08-16 18:44:35.09782	\N
e47aa713-f22d-4cf4-a1b1-a5538aa360c4	7bd48e2f-0f1e-4f81-9d08-f72088d6b345	{"field_63dc85c4": "magoosh-gre-1000-words_oct01.pdf", "field_79735ce7": "Grace Irish", "field_79923580": 25, "field_ae8458f4": "Belfast", "field_f50a7fd0": "M.s.c  Chemistry"}	2026-08-22 11:49:04.416971	\N
fe84e1b9-2e17-4db3-b2b1-482930dcad25	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:04:16.928496	\N
b273c536-8081-43e9-9450-3b4a8acb1b94	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:04:20.550219	\N
c457d97c-a470-4b92-8e9e-67b85fe4b0ae	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:05:35.532287	\N
769253a5-417b-4268-942b-495faee19716	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:05:36.200908	\N
f919e215-3b5e-4c17-9f5d-705727b4e868	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:05:36.348742	\N
1ec4cf95-6b25-4ce7-9c0a-0266dec64921	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:05:36.600629	\N
8580d0c9-d2dc-4e3d-a146-e88f2d17dc50	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:05:36.749661	\N
94346f7b-3e1c-47bd-b418-f82396e6dfff	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:05:36.901249	\N
757028dc-dabc-4c81-96af-d6c3af26b316	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:05:37.034735	\N
adb43682-0c4e-4ec7-ac95-00dff14ecc22	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:05:37.200626	\N
8588e050-7116-448e-9ebd-5fd3737dd1b8	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:05:47.968675	\N
96af27a7-c87c-4f4f-84c6-c294c91cd1e3	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:41.653066	\N
0da23e7c-4d36-442b-9864-5aec5286bedc	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:41.865922	\N
10c65c43-3dce-44b3-aebe-a7a317656a39	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:42.166188	\N
03ad50e4-c49d-4a0f-a880-3e7d5854627b	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:42.382666	\N
e33cbf3b-5dfb-40f0-b041-93cad2abf7b8	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:42.56691	\N
19b47cf6-bbb7-4bd9-a981-cd6e8356bdb4	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:42.861286	\N
a5a237b3-f064-45ff-aa23-37cf3529f9ba	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:43.148936	\N
ef81769f-842a-428d-9330-461cbbbf2ce5	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:43.333928	\N
4c56c915-b892-4172-8b8f-dac5e2d99fd7	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:43.795055	\N
2184d1ed-0a11-4ec2-bf85-66793bcd4159	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:43.982661	\N
7069b703-6e4b-4a90-9e20-82226323563f	4a204778-b280-4253-a1ce-75d79d35421d	{}	2026-08-22 13:09:44.165164	\N
cd20c462-d6e2-4df2-85f5-a7d5722d34f2	7bd48e2f-0f1e-4f81-9d08-f72088d6b345	{"field_63dc85c4": "magoosh-gre-1000-words_oct01.pdf", "field_79735ce7": "Grace Irish", "field_79923580": 25, "field_ae8458f4": "Belfast", "field_f50a7fd0": "M.s.c Chemistry"}	2026-08-23 08:10:34.935846	\N
77d02578-182e-40ba-abb1-7ea46cab65d2	aaf4be30-4ebc-498a-9752-494405f3b6df	{}	2026-08-23 08:50:56.911716	e070c24d-49d6-4a07-8ce5-28eb10d111e4
298b451d-ac01-40cd-811e-abc4deb0a916	eb106bea-c177-419b-a660-1512c2501b1f	{"field_6031041c": "prashant.shaw@tcs.com", "field_742064c9": "Chiranjeev_Resume_switch (8).pdf", "field_a012efdd": 28, "field_a4b295ab": 2018, "field_d2c89978": 8.2, "field_e070ec08": "Prashant Shaw"}	2026-08-23 08:52:30.448384	7d4c944a-cb4e-401a-9e4d-6e90def53bf3
f07b741d-3554-4799-b02c-950247523d4a	dad3c27a-8f1a-4727-a238-737640635f7b	{"field_6eb43d48": "Chiranjeev_Resume_switch (10) (1).pdf", "field_92632ecd": "Amit Kumar", "field_ad72fc94": "3", "field_b2c49d2e": "23-10-2024", "field_b37c5980": 26}	2026-08-23 08:54:29.337834	ccd9581a-673f-403f-b9b4-320c383fa9dd
27f4133a-f6ee-46e3-af48-274554523917	e695051f-4b36-4173-839e-0de2e894b725	{"field_1d8327b6": 2948341, "field_50f9c2b9": true, "field_5a16a08c": "C:\\\\fakepath\\\\e0b229a5-0ba5-422d-aa23-0e5369dd3644.pdf", "field_ed6e57a1": "Medhavi Bidhuri"}	2026-08-23 12:24:00.246429	76f3818e-5da5-4700-968a-9285d45a4748
a51b2e4f-ed42-4de8-8542-cc9a85bb2c1b	6196b179-76f2-4ea2-a64e-9cdce60e178a	{"field_8ef976a7": "Sangeeta Mishra", "field_bccd6727": 2804565, "field_ea5f2f39": true, "field_fe5797fb": "BLR_GOX_26062026_27134258668.pdf"}	2026-08-30 12:32:48.990058	22710186-985b-44b2-8d29-2779818554d0
\.


--
-- Data for Name: organization; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.organization (id, name) FROM stdin;
85792f0f-e64d-4e6c-a354-fced69307022	evalueserve.inc
03854879-49d0-49fc-ada4-3b037c11bb48	peaky blinders uk
c6439e66-bd32-4bf0-ac86-9281239463f8	tata consultancy services
d88b63c4-48ba-4651-bfb9-f63a34f3605c	netflix test corp
40dc9450-afe9-4bca-87ce-5a7c4cd93aae	accenture
8112cdf3-0d50-4f1a-89b9-f925a7ff355c	zoho inc
2314f35e-f9f0-4304-a19c-0766b6f9a197	euphoria inc
\.


--
-- Data for Name: organizationinvite; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.organizationinvite (id, organization_id, role, used_at, created_at) FROM stdin;
d17ede80-1eec-4b95-ae19-eef0c75d1610	8112cdf3-0d50-4f1a-89b9-f925a7ff355c	member	2026-08-23 12:23:24.106249	2026-08-23 12:16:32.731803
294f13e9-2f3f-4dc0-9552-2c1d2698c166	2314f35e-f9f0-4304-a19c-0766b6f9a197	member	2026-08-23 12:54:13.769943	2026-08-23 12:53:11.512557
8036a97d-2f74-4383-8638-a766c1871c7f	2314f35e-f9f0-4304-a19c-0766b6f9a197	member	2026-08-30 10:57:35.924459	2026-08-30 10:56:02.313088
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."user" (id, email, hashed_password, organization_id, role) FROM stdin;
e070c24d-49d6-4a07-8ce5-28eb10d111e4	sethi.chiranjeev@tcs.com	$argon2id$v=19$m=65536,t=3,p=4$/+gr0jhszDNapIlml8lGbQ$j7TEkMrsQDw3Lvvrb3DDzimZWkY89dbSft91yjjX6DQ	c6439e66-bd32-4bf0-ac86-9281239463f8	member
bc94c872-fc7c-47aa-9c63-6dfb96bf9217	grace_irish@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$hfk4KQi5W2trzWs12SCd/Q$HvDPdif9A1w4l2+0ZCE6TmE6oT0k/kwGvjfJv2rcrCU	03854879-49d0-49fc-ada4-3b037c11bb48	member
7ded88f3-2ed4-45ec-9e3f-f1b2e96b85c1	arthur_shelby@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$vWRVkw20lqV/mTHgYWhHTA$7bs1ilZpKQyZAJ+PMjzj/TgmOVm7p9xF8xme6xyDAHs	03854879-49d0-49fc-ada4-3b037c11bb48	member
ccd9581a-673f-403f-b9b4-320c383fa9dd	amit.kumar@accenture.com	$argon2id$v=19$m=65536,t=3,p=4$CA0f3fFpL0nQCCijbCzilw$RyM1H85BfRfLGbiaae8m7CRfNckH3coaZJ8kDvwQjvc	40dc9450-afe9-4bca-87ce-5a7c4cd93aae	member
a21e2d15-14de-464a-bb04-5587137b028d	sridhar.vembu@zoho.com	$argon2id$v=19$m=65536,t=3,p=4$ZrkJ+qP1UCJilE+rmw98nQ$v7ljs2BBm3poojwdoiHr7RrOiDkSwd52z9rQczswqQI	8112cdf3-0d50-4f1a-89b9-f925a7ff355c	member
d9d85cdb-f9dc-4faf-a907-4690b8fdce45	ankit.kumar@zoho.com	$argon2id$v=19$m=65536,t=3,p=4$vlBrpbkL3ZWvLEtgmxGrLw$GfuUf8ANpq35ImZOJ9YDMUtNboeYCjHvBAXLNskOOBA	8112cdf3-0d50-4f1a-89b9-f925a7ff355c	member
91bc5811-da95-44cf-ab99-874fa91b94b7	admin@netflix.com	$argon2id$v=19$m=65536,t=3,p=4$h9muDWKnLORiSsvj0Mshtw$vWfx7NC9653DPAV0h9eH0/L6jIv7XWWwFFLPfXRerBQ	d88b63c4-48ba-4651-bfb9-f63a34f3605c	owner
c4001d56-37b7-47bb-86ca-e3fbdf0ee2e1	random@evalueserve.com	$argon2id$v=19$m=65536,t=3,p=4$xZuwcHQktKn9HZY4uyu5uw$ALjSfj4iS5chBJb8NZu2+L0dZ3gVGqRStd1TAjNziAc	85792f0f-e64d-4e6c-a354-fced69307022	owner
4845beb7-ada5-4305-a824-3aae3a62ead5	campbell.wilson789@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$6Bnfp//LdfaIhzbCUZdgHg$7bxlZnzsAO70Cmur9eKmPnrWTssxafr6shFwCfjAaUc	03854879-49d0-49fc-ada4-3b037c11bb48	owner
7d4c944a-cb4e-401a-9e4d-6e90def53bf3	prashant.shaw@tcs.com	$argon2id$v=19$m=65536,t=3,p=4$71wAItdD5yZ0s6Gl9bqUrw$YydedA3JAYt2fBuQeUb/MrOnd8rkm89vctM69/XH/kY	c6439e66-bd32-4bf0-ac86-9281239463f8	owner
48e1b310-a296-4275-b5a5-b2b7bd9cb981	amit.singh@accenture.com	$argon2id$v=19$m=65536,t=3,p=4$eDhX1ypmRFsPqOMa6icz3A$Dm+bkdmzBQQdKB+Nx7G8KzjUrHfXWgBdzggbTRnPXiY	40dc9450-afe9-4bca-87ce-5a7c4cd93aae	owner
0df0cb9f-1e4a-41f0-8ad5-c9d8627e012e	sumit.singh@zoho.com	$argon2id$v=19$m=65536,t=3,p=4$DGNeZq45ErHMm0BmIgulHw$GKkTm3UwOevBcdh6Vt+iySYhtc2VSk1F5jMxqaM99F8	8112cdf3-0d50-4f1a-89b9-f925a7ff355c	owner
76f3818e-5da5-4700-968a-9285d45a4748	medhavi.bd@zoho.com	$argon2id$v=19$m=65536,t=3,p=4$wdMxC1jnMLrlb/RmQhyZOA$Q4gEb6F8qfPzWuehqs+wu0FEQl5sxww6v2uECpdkoDc	8112cdf3-0d50-4f1a-89b9-f925a7ff355c	member
85a13a7d-9d35-43b5-8b19-89e7b64e75f0	faizal.ali@euphoria.com	$argon2id$v=19$m=65536,t=3,p=4$qWn+23UuA8C1vMlYZ873CQ$f2MggmMKDGh/hryS8wYJ+neZEosTnIlYn8hg9W8xT8g	2314f35e-f9f0-4304-a19c-0766b6f9a197	owner
9e0f641a-8c6d-4e15-a676-eed2f8ded233	jairam.singh@euphoria.com	$argon2id$v=19$m=65536,t=3,p=4$4+CZWqiFu+0/m9CC/NVpdg$2YF4Vv2//dx47dpi6gu+cRNFFXVr+LQx5YckjTkcZ7c	2314f35e-f9f0-4304-a19c-0766b6f9a197	member
22710186-985b-44b2-8d29-2779818554d0	sangeeta.mishra@euphoria.com	$argon2id$v=19$m=65536,t=3,p=4$AgJG8FKB6hw777Mh0Cbp1Q$sx7gQjTyqFVW2KGgo1JheFBX/BlCgbrdHKa7ZWvrn5g	2314f35e-f9f0-4304-a19c-0766b6f9a197	member
\.


--
-- Name: fileattachment fileattachment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fileattachment
    ADD CONSTRAINT fileattachment_pkey PRIMARY KEY (id);


--
-- Name: fileattachment fileattachment_storage_path_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fileattachment
    ADD CONSTRAINT fileattachment_storage_path_key UNIQUE (storage_path);


--
-- Name: form form_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.form
    ADD CONSTRAINT form_pkey PRIMARY KEY (id);


--
-- Name: formsubmission formsubmission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.formsubmission
    ADD CONSTRAINT formsubmission_pkey PRIMARY KEY (id);


--
-- Name: organization organization_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organization
    ADD CONSTRAINT organization_pkey PRIMARY KEY (id);


--
-- Name: organizationinvite organizationinvite_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organizationinvite
    ADD CONSTRAINT organizationinvite_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: ix_fileattachment_submission_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_fileattachment_submission_id ON public.fileattachment USING btree (submission_id);


--
-- Name: ix_form_title; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_form_title ON public.form USING btree (title);


--
-- Name: ix_formsubmission_form_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_formsubmission_form_id ON public.formsubmission USING btree (form_id);


--
-- Name: ix_organizationinvite_organization_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_organizationinvite_organization_id ON public.organizationinvite USING btree (organization_id);


--
-- Name: ix_user_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_user_email ON public."user" USING btree (email);


--
-- Name: uq_formsubmission_user; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_formsubmission_user ON public.formsubmission USING btree (form_id, submitted_by_user_id) WHERE (submitted_by_user_id IS NOT NULL);


--
-- Name: uq_organization_normalized_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_organization_normalized_name ON public.organization USING btree (lower(btrim((name)::text)));


--
-- Name: fileattachment fileattachment_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fileattachment
    ADD CONSTRAINT fileattachment_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.formsubmission(id);


--
-- Name: form form_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.form
    ADD CONSTRAINT form_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public."user"(id);


--
-- Name: form form_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.form
    ADD CONSTRAINT form_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organization(id);


--
-- Name: formsubmission formsubmission_form_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.formsubmission
    ADD CONSTRAINT formsubmission_form_id_fkey FOREIGN KEY (form_id) REFERENCES public.form(id);


--
-- Name: formsubmission formsubmission_submitted_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.formsubmission
    ADD CONSTRAINT formsubmission_submitted_by_user_id_fkey FOREIGN KEY (submitted_by_user_id) REFERENCES public."user"(id);


--
-- Name: organizationinvite organizationinvite_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organizationinvite
    ADD CONSTRAINT organizationinvite_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organization(id);


--
-- Name: user user_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organization(id);


--
-- PostgreSQL database dump complete
--

\unrestrict avl2XMLcPPk2e45YzoELIGsbIOLVVQ0w18aLoMbtg63fkzC0dATYnWzT1mqLhj6


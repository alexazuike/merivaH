PGDMP         7                z            healthAppPH    14.4 #   14.3 (Ubuntu 14.3-0ubuntu0.22.04.1) �   #           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            $           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            %           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            &           1262    23780    healthAppPH    DATABASE     b   CREATE DATABASE "healthAppPH" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.UTF-8';
    DROP DATABASE "healthAppPH";
                doadmin    false            �            1259    23807 
   auth_group    TABLE     f   CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);
    DROP TABLE public.auth_group;
       public         heap    health    false            �            1259    23806    auth_group_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.auth_group_id_seq;
       public          health    false    216            '           0    0    auth_group_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;
          public          health    false    215            �            1259    23816    auth_group_permissions    TABLE     �   CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);
 *   DROP TABLE public.auth_group_permissions;
       public         heap    health    false            �            1259    23815    auth_group_permissions_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.auth_group_permissions_id_seq;
       public          health    false    218            (           0    0    auth_group_permissions_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;
          public          health    false    217            �            1259    23800    auth_permission    TABLE     �   CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);
 #   DROP TABLE public.auth_permission;
       public         heap    health    false            �            1259    23799    auth_permission_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.auth_permission_id_seq;
       public          health    false    214            )           0    0    auth_permission_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;
          public          health    false    213            �            1259    23823 	   auth_user    TABLE     �  CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);
    DROP TABLE public.auth_user;
       public         heap    health    false            �            1259    23832    auth_user_groups    TABLE     ~   CREATE TABLE public.auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);
 $   DROP TABLE public.auth_user_groups;
       public         heap    health    false            �            1259    23831    auth_user_groups_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.auth_user_groups_id_seq;
       public          health    false    222            *           0    0    auth_user_groups_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.auth_user_groups_id_seq OWNED BY public.auth_user_groups.id;
          public          health    false    221            �            1259    23822    auth_user_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.auth_user_id_seq;
       public          health    false    220            +           0    0    auth_user_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.auth_user_id_seq OWNED BY public.auth_user.id;
          public          health    false    219            �            1259    23839    auth_user_user_permissions    TABLE     �   CREATE TABLE public.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);
 .   DROP TABLE public.auth_user_user_permissions;
       public         heap    health    false            �            1259    23838 !   auth_user_user_permissions_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.auth_user_user_permissions_id_seq;
       public          health    false    224            ,           0    0 !   auth_user_user_permissions_id_seq    SEQUENCE OWNED BY     g   ALTER SEQUENCE public.auth_user_user_permissions_id_seq OWNED BY public.auth_user_user_permissions.id;
          public          health    false    223            �            1259    23927    authtoken_token    TABLE     �   CREATE TABLE public.authtoken_token (
    key character varying(40) NOT NULL,
    created timestamp with time zone NOT NULL,
    user_id integer NOT NULL
);
 #   DROP TABLE public.authtoken_token;
       public         heap    health    false            �            1259    24029    constance_config    TABLE     {   CREATE TABLE public.constance_config (
    id integer NOT NULL,
    key character varying(255) NOT NULL,
    value text
);
 $   DROP TABLE public.constance_config;
       public         heap    health    false            �            1259    24028    constance_config_id_seq    SEQUENCE     �   CREATE SEQUENCE public.constance_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.constance_config_id_seq;
       public          health    false    249            -           0    0    constance_config_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.constance_config_id_seq OWNED BY public.constance_config.id;
          public          health    false    248            �            1259    23941    core_country    TABLE     a   CREATE TABLE public.core_country (
    id bigint NOT NULL,
    country character varying(255)
);
     DROP TABLE public.core_country;
       public         heap    health    false            �            1259    23940    core_country_id_seq    SEQUENCE     |   CREATE SEQUENCE public.core_country_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.core_country_id_seq;
       public          health    false    229            .           0    0    core_country_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.core_country_id_seq OWNED BY public.core_country.id;
          public          health    false    228            �            1259    23997    core_district    TABLE     �   CREATE TABLE public.core_district (
    id bigint NOT NULL,
    district character varying(255),
    state_id bigint NOT NULL
);
 !   DROP TABLE public.core_district;
       public         heap    health    false            �            1259    23996    core_district_id_seq    SEQUENCE     }   CREATE SEQUENCE public.core_district_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.core_district_id_seq;
       public          health    false    245            /           0    0    core_district_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.core_district_id_seq OWNED BY public.core_district.id;
          public          health    false    244            �            1259    23948    core_gender    TABLE     _   CREATE TABLE public.core_gender (
    id bigint NOT NULL,
    gender character varying(255)
);
    DROP TABLE public.core_gender;
       public         heap    health    false            �            1259    23947    core_gender_id_seq    SEQUENCE     {   CREATE SEQUENCE public.core_gender_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.core_gender_id_seq;
       public          health    false    231            0           0    0    core_gender_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.core_gender_id_seq OWNED BY public.core_gender.id;
          public          health    false    230            �            1259    24022    core_identity    TABLE     h   CREATE TABLE public.core_identity (
    id bigint NOT NULL,
    name character varying(200) NOT NULL
);
 !   DROP TABLE public.core_identity;
       public         heap    health    false            �            1259    24021    core_identity_id_seq    SEQUENCE     }   CREATE SEQUENCE public.core_identity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.core_identity_id_seq;
       public          health    false    247            1           0    0    core_identity_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.core_identity_id_seq OWNED BY public.core_identity.id;
          public          health    false    246            �            1259    23990    core_lga    TABLE     w   CREATE TABLE public.core_lga (
    id bigint NOT NULL,
    lga character varying(255),
    state_id bigint NOT NULL
);
    DROP TABLE public.core_lga;
       public         heap    health    false            �            1259    23989    core_lga_id_seq    SEQUENCE     x   CREATE SEQUENCE public.core_lga_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.core_lga_id_seq;
       public          health    false    243            2           0    0    core_lga_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.core_lga_id_seq OWNED BY public.core_lga.id;
          public          health    false    242            �            1259    23955    core_maritalstatus    TABLE     n   CREATE TABLE public.core_maritalstatus (
    id bigint NOT NULL,
    marital_status character varying(255)
);
 &   DROP TABLE public.core_maritalstatus;
       public         heap    health    false            �            1259    23954    core_maritalstatus_id_seq    SEQUENCE     �   CREATE SEQUENCE public.core_maritalstatus_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.core_maritalstatus_id_seq;
       public          health    false    233            3           0    0    core_maritalstatus_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.core_maritalstatus_id_seq OWNED BY public.core_maritalstatus.id;
          public          health    false    232            �            1259    23962    core_occupation    TABLE     g   CREATE TABLE public.core_occupation (
    id bigint NOT NULL,
    occupation character varying(255)
);
 #   DROP TABLE public.core_occupation;
       public         heap    health    false            �            1259    23961    core_occupation_id_seq    SEQUENCE        CREATE SEQUENCE public.core_occupation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.core_occupation_id_seq;
       public          health    false    235            4           0    0    core_occupation_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.core_occupation_id_seq OWNED BY public.core_occupation.id;
          public          health    false    234            �            1259    23969    core_religion    TABLE     c   CREATE TABLE public.core_religion (
    id bigint NOT NULL,
    religion character varying(255)
);
 !   DROP TABLE public.core_religion;
       public         heap    health    false            �            1259    23968    core_religion_id_seq    SEQUENCE     }   CREATE SEQUENCE public.core_religion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.core_religion_id_seq;
       public          health    false    237            5           0    0    core_religion_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.core_religion_id_seq OWNED BY public.core_religion.id;
          public          health    false    236            �            1259    23976    core_salutation    TABLE     g   CREATE TABLE public.core_salutation (
    id bigint NOT NULL,
    salutations character varying(50)
);
 #   DROP TABLE public.core_salutation;
       public         heap    health    false            �            1259    23975    core_salutation_id_seq    SEQUENCE        CREATE SEQUENCE public.core_salutation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.core_salutation_id_seq;
       public          health    false    239            6           0    0    core_salutation_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.core_salutation_id_seq OWNED BY public.core_salutation.id;
          public          health    false    238            �            1259    23983 
   core_state    TABLE     }   CREATE TABLE public.core_state (
    id bigint NOT NULL,
    state character varying(255),
    country_id bigint NOT NULL
);
    DROP TABLE public.core_state;
       public         heap    health    false            �            1259    23982    core_state_id_seq    SEQUENCE     z   CREATE SEQUENCE public.core_state_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.core_state_id_seq;
       public          health    false    241            7           0    0    core_state_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.core_state_id_seq OWNED BY public.core_state.id;
          public          health    false    240            �            1259    23898    django_admin_log    TABLE     �  CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);
 $   DROP TABLE public.django_admin_log;
       public         heap    health    false            �            1259    23897    django_admin_log_id_seq    SEQUENCE     �   CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.django_admin_log_id_seq;
       public          health    false    226            8           0    0    django_admin_log_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;
          public          health    false    225            �            1259    23791    django_content_type    TABLE     �   CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);
 '   DROP TABLE public.django_content_type;
       public         heap    health    false            �            1259    23790    django_content_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.django_content_type_id_seq;
       public          health    false    212            9           0    0    django_content_type_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;
          public          health    false    211            �            1259    23782    django_migrations    TABLE     �   CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);
 %   DROP TABLE public.django_migrations;
       public         heap    health    false            �            1259    23781    django_migrations_id_seq    SEQUENCE     �   CREATE SEQUENCE public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.django_migrations_id_seq;
       public          health    false    210            :           0    0    django_migrations_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;
          public          health    false    209            .           1259    24451    django_session    TABLE     �   CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);
 "   DROP TABLE public.django_session;
       public         heap    health    false                       1259    24080    encounters_clinic    TABLE     �   CREATE TABLE public.encounters_clinic (
    id bigint NOT NULL,
    name character varying(50) NOT NULL,
    is_active boolean NOT NULL,
    "Department_id" bigint NOT NULL,
    bill_item_code character varying(50)
);
 %   DROP TABLE public.encounters_clinic;
       public         heap    health    false                       1259    24079    encounters_clinic_id_seq    SEQUENCE     �   CREATE SEQUENCE public.encounters_clinic_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.encounters_clinic_id_seq;
       public          health    false    259            ;           0    0    encounters_clinic_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.encounters_clinic_id_seq OWNED BY public.encounters_clinic.id;
          public          health    false    258                       1259    24071    encounters_encounter    TABLE     O  CREATE TABLE public.encounters_encounter (
    id bigint NOT NULL,
    encounter_id character varying(50) NOT NULL,
    clinic jsonb NOT NULL,
    time_log jsonb NOT NULL,
    chart jsonb NOT NULL,
    provider jsonb NOT NULL,
    patient jsonb NOT NULL,
    is_active boolean NOT NULL,
    status character varying(200),
    encounter_type character varying(255) NOT NULL,
    encounter_datetime timestamp with time zone NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    chief_complaint text,
    bill character varying(255),
    signed_date timestamp with time zone
);
 (   DROP TABLE public.encounters_encounter;
       public         heap    health    false                        1259    24070    encounters_encounter_id_seq    SEQUENCE     �   CREATE SEQUENCE public.encounters_encounter_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.encounters_encounter_id_seq;
       public          health    false    257            <           0    0    encounters_encounter_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.encounters_encounter_id_seq OWNED BY public.encounters_encounter.id;
          public          health    false    256                       1259    24111    encounters_encounter_type    TABLE     s   CREATE TABLE public.encounters_encounter_type (
    id bigint NOT NULL,
    name character varying(50) NOT NULL
);
 -   DROP TABLE public.encounters_encounter_type;
       public         heap    health    false                       1259    24110     encounters_encounter_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.encounters_encounter_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.encounters_encounter_type_id_seq;
       public          health    false    261            =           0    0     encounters_encounter_type_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.encounters_encounter_type_id_seq OWNED BY public.encounters_encounter_type.id;
          public          health    false    260            �            1259    24062    encounters_status    TABLE     k   CREATE TABLE public.encounters_status (
    id bigint NOT NULL,
    name character varying(50) NOT NULL
);
 %   DROP TABLE public.encounters_status;
       public         heap    health    false            �            1259    24061    encounters_status_id_seq    SEQUENCE     �   CREATE SEQUENCE public.encounters_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.encounters_status_id_seq;
       public          health    false    255            >           0    0    encounters_status_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.encounters_status_id_seq OWNED BY public.encounters_status.id;
          public          health    false    254            �            1259    24041    facilities_department    TABLE     �   CREATE TABLE public.facilities_department (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    description text NOT NULL,
    display_name character varying(255) NOT NULL,
    is_active boolean NOT NULL
);
 )   DROP TABLE public.facilities_department;
       public         heap    health    false            �            1259    24040    facilities_department_id_seq    SEQUENCE     �   CREATE SEQUENCE public.facilities_department_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.facilities_department_id_seq;
       public          health    false    251            ?           0    0    facilities_department_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.facilities_department_id_seq OWNED BY public.facilities_department.id;
          public          health    false    250            �            1259    24050    facilities_facility    TABLE     �  CREATE TABLE public.facilities_facility (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    address jsonb NOT NULL,
    state character varying(255) NOT NULL,
    city character varying(255) NOT NULL,
    lga character varying(255) NOT NULL,
    phone character varying(255) NOT NULL,
    email character varying(254) NOT NULL,
    facility_code character varying(254) NOT NULL,
    is_active boolean NOT NULL
);
 '   DROP TABLE public.facilities_facility;
       public         heap    health    false            �            1259    24049    facilities_facility_id_seq    SEQUENCE     �   CREATE SEQUENCE public.facilities_facility_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.facilities_facility_id_seq;
       public          health    false    253            @           0    0    facilities_facility_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.facilities_facility_id_seq OWNED BY public.facilities_facility.id;
          public          health    false    252                       1259    24208    finance_bill    TABLE     �  CREATE TABLE public.finance_bill (
    id bigint NOT NULL,
    bill_item_code character varying(256) NOT NULL,
    cost_price numeric(10,2) NOT NULL,
    selling_price numeric(10,2) NOT NULL,
    cleared_status character varying(256) NOT NULL,
    quantity integer NOT NULL,
    bill_source character varying(256) NOT NULL,
    billed_to_type character varying(256) NOT NULL,
    service_center character varying(256),
    description text,
    is_service_rendered boolean NOT NULL,
    is_invoiced boolean NOT NULL,
    transaction_date timestamp with time zone NOT NULL,
    billed_to_id bigint,
    co_pay numeric(10,2),
    auth_code character varying(256),
    is_capitated boolean NOT NULL,
    patient jsonb NOT NULL
);
     DROP TABLE public.finance_bill;
       public         heap    health    false                       1259    24207    finance_bill_id_seq    SEQUENCE     |   CREATE SEQUENCE public.finance_bill_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.finance_bill_id_seq;
       public          health    false    273            A           0    0    finance_bill_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.finance_bill_id_seq OWNED BY public.finance_bill.id;
          public          health    false    272                       1259    24141    finance_billableitem    TABLE     �  CREATE TABLE public.finance_billableitem (
    id bigint NOT NULL,
    item_code character varying(256) NOT NULL,
    description character varying(256),
    cost numeric(10,2),
    selling_price numeric(10,2),
    module character varying(256) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    created_by jsonb NOT NULL,
    updated_by jsonb NOT NULL
);
 (   DROP TABLE public.finance_billableitem;
       public         heap    health    false                       1259    24140    finance_billableitem_id_seq    SEQUENCE     �   CREATE SEQUENCE public.finance_billableitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.finance_billableitem_id_seq;
       public          health    false    263            B           0    0    finance_billableitem_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.finance_billableitem_id_seq OWNED BY public.finance_billableitem.id;
          public          health    false    262            	           1259    24152    finance_payer    TABLE     �   CREATE TABLE public.finance_payer (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    address character varying(256),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
 !   DROP TABLE public.finance_payer;
       public         heap    health    false                       1259    24151    finance_payer_id_seq    SEQUENCE     }   CREATE SEQUENCE public.finance_payer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.finance_payer_id_seq;
       public          health    false    265            C           0    0    finance_payer_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.finance_payer_id_seq OWNED BY public.finance_payer.id;
          public          health    false    264                       1259    24179    finance_payerscheme    TABLE     {  CREATE TABLE public.finance_payerscheme (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    created_by jsonb NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_by jsonb NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    payer_id bigint NOT NULL,
    price_list_id bigint NOT NULL,
    type character varying(256) NOT NULL
);
 '   DROP TABLE public.finance_payerscheme;
       public         heap    health    false                       1259    24178    finance_payerscheme_id_seq    SEQUENCE     �   CREATE SEQUENCE public.finance_payerscheme_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.finance_payerscheme_id_seq;
       public          health    false    271            D           0    0    finance_payerscheme_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.finance_payerscheme_id_seq OWNED BY public.finance_payerscheme.id;
          public          health    false    270            0           1259    24504    finance_payment    TABLE       CREATE TABLE public.finance_payment (
    id bigint NOT NULL,
    bills jsonb NOT NULL,
    patient jsonb NOT NULL,
    total_amount numeric(10,2) NOT NULL,
    audit_log jsonb NOT NULL,
    created_at timestamp with time zone NOT NULL,
    payment_method_id bigint
);
 #   DROP TABLE public.finance_payment;
       public         heap    health    false            /           1259    24503    finance_payment_id_seq    SEQUENCE        CREATE SEQUENCE public.finance_payment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.finance_payment_id_seq;
       public          health    false    304            E           0    0    finance_payment_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.finance_payment_id_seq OWNED BY public.finance_payment.id;
          public          health    false    303            2           1259    24529    finance_paymentmethod    TABLE     �   CREATE TABLE public.finance_paymentmethod (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    description character varying(256),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
 )   DROP TABLE public.finance_paymentmethod;
       public         heap    health    false            1           1259    24528    finance_paymentmethod_id_seq    SEQUENCE     �   CREATE SEQUENCE public.finance_paymentmethod_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.finance_paymentmethod_id_seq;
       public          health    false    306            F           0    0    finance_paymentmethod_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.finance_paymentmethod_id_seq OWNED BY public.finance_paymentmethod.id;
          public          health    false    305                       1259    24161    finance_pricelist    TABLE     O  CREATE TABLE public.finance_pricelist (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    description character varying(256),
    created_by jsonb NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_by jsonb NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    meta jsonb NOT NULL
);
 %   DROP TABLE public.finance_pricelist;
       public         heap    health    false            
           1259    24160    finance_pricelist_id_seq    SEQUENCE     �   CREATE SEQUENCE public.finance_pricelist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.finance_pricelist_id_seq;
       public          health    false    267            G           0    0    finance_pricelist_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.finance_pricelist_id_seq OWNED BY public.finance_pricelist.id;
          public          health    false    266                       1259    24170    finance_pricelistitem    TABLE     �  CREATE TABLE public.finance_pricelistitem (
    id bigint NOT NULL,
    bill_item_code character varying(256) NOT NULL,
    selling_price numeric(10,2) NOT NULL,
    co_pay jsonb NOT NULL,
    is_auth_req boolean NOT NULL,
    is_capitated boolean NOT NULL,
    created_by jsonb NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_by jsonb NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    price_list_id bigint NOT NULL
);
 )   DROP TABLE public.finance_pricelistitem;
       public         heap    health    false                       1259    24169    finance_pricelistitem_id_seq    SEQUENCE     �   CREATE SEQUENCE public.finance_pricelistitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.finance_pricelistitem_id_seq;
       public          health    false    269            H           0    0    finance_pricelistitem_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.finance_pricelistitem_id_seq OWNED BY public.finance_pricelistitem.id;
          public          health    false    268                       1259    24268    imaging_imagingobservation    TABLE     H  CREATE TABLE public.imaging_imagingobservation (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    active boolean NOT NULL,
    status character varying(256),
    audit_log jsonb,
    created_at timestamp with time zone NOT NULL,
    img_unit_id bigint NOT NULL,
    bill_item_code character varying(256)
);
 .   DROP TABLE public.imaging_imagingobservation;
       public         heap    health    false                       1259    24267 !   imaging_imagingobservation_id_seq    SEQUENCE     �   CREATE SEQUENCE public.imaging_imagingobservation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.imaging_imagingobservation_id_seq;
       public          health    false    283            I           0    0 !   imaging_imagingobservation_id_seq    SEQUENCE OWNED BY     g   ALTER SEQUENCE public.imaging_imagingobservation_id_seq OWNED BY public.imaging_imagingobservation.id;
          public          health    false    282                       1259    24259    imaging_imagingobservationorder    TABLE     5  CREATE TABLE public.imaging_imagingobservationorder (
    id bigint NOT NULL,
    img_obv jsonb NOT NULL,
    status character varying(256),
    audit_log jsonb,
    created_at timestamp with time zone NOT NULL,
    img_order_id bigint NOT NULL,
    patient jsonb NOT NULL,
    bill character varying(256)
);
 3   DROP TABLE public.imaging_imagingobservationorder;
       public         heap    health    false                       1259    24258 &   imaging_imagingobservationorder_id_seq    SEQUENCE     �   CREATE SEQUENCE public.imaging_imagingobservationorder_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 =   DROP SEQUENCE public.imaging_imagingobservationorder_id_seq;
       public          health    false    281            J           0    0 &   imaging_imagingobservationorder_id_seq    SEQUENCE OWNED BY     q   ALTER SEQUENCE public.imaging_imagingobservationorder_id_seq OWNED BY public.imaging_imagingobservationorder.id;
          public          health    false    280                       1259    24234    imaging_imagingorder    TABLE     �  CREATE TABLE public.imaging_imagingorder (
    id bigint NOT NULL,
    patient jsonb NOT NULL,
    img_id character varying(256) NOT NULL,
    stat boolean NOT NULL,
    service_center jsonb NOT NULL,
    referral_facility jsonb,
    comments text,
    img_obv jsonb NOT NULL,
    img_obv_orders jsonb NOT NULL,
    ordered_by jsonb NOT NULL,
    ordered_datetime timestamp with time zone NOT NULL,
    ordering_physician character varying(256)
);
 (   DROP TABLE public.imaging_imagingorder;
       public         heap    health    false                       1259    24233    imaging_imagingorder_id_seq    SEQUENCE     �   CREATE SEQUENCE public.imaging_imagingorder_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.imaging_imagingorder_id_seq;
       public          health    false    275            K           0    0    imaging_imagingorder_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.imaging_imagingorder_id_seq OWNED BY public.imaging_imagingorder.id;
          public          health    false    274                       1259    24245    imaging_imagingunit    TABLE     �   CREATE TABLE public.imaging_imagingunit (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    order_no integer NOT NULL,
    created_at timestamp with time zone NOT NULL
);
 '   DROP TABLE public.imaging_imagingunit;
       public         heap    health    false                       1259    24244    imaging_labunit_id_seq    SEQUENCE        CREATE SEQUENCE public.imaging_labunit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.imaging_labunit_id_seq;
       public          health    false    277            L           0    0    imaging_labunit_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.imaging_labunit_id_seq OWNED BY public.imaging_imagingunit.id;
          public          health    false    276                       1259    24252    imaging_servicecenter    TABLE     �   CREATE TABLE public.imaging_servicecenter (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp with time zone NOT NULL
);
 )   DROP TABLE public.imaging_servicecenter;
       public         heap    health    false                       1259    24251    imaging_servicecenter_id_seq    SEQUENCE     �   CREATE SEQUENCE public.imaging_servicecenter_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.imaging_servicecenter_id_seq;
       public          health    false    279            M           0    0    imaging_servicecenter_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.imaging_servicecenter_id_seq OWNED BY public.imaging_servicecenter.id;
          public          health    false    278                       1259    24313    laboratory_labobservation    TABLE       CREATE TABLE public.laboratory_labobservation (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    uom character varying(256) NOT NULL,
    reference_range jsonb NOT NULL,
    type jsonb NOT NULL,
    created_at timestamp with time zone NOT NULL
);
 -   DROP TABLE public.laboratory_labobservation;
       public         heap    health    false                       1259    24312     laboratory_labobservation_id_seq    SEQUENCE     �   CREATE SEQUENCE public.laboratory_labobservation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.laboratory_labobservation_id_seq;
       public          health    false    285            N           0    0     laboratory_labobservation_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.laboratory_labobservation_id_seq OWNED BY public.laboratory_labobservation.id;
          public          health    false    284            #           1259    24338    laboratory_laborder    TABLE     �  CREATE TABLE public.laboratory_laborder (
    id bigint NOT NULL,
    patient jsonb NOT NULL,
    asn character varying(80) NOT NULL,
    stat boolean NOT NULL,
    service_center jsonb NOT NULL,
    referral_facility jsonb,
    comments text,
    ordered_by jsonb NOT NULL,
    ordered_datetime timestamp with time zone NOT NULL,
    lab_panel_orders jsonb NOT NULL,
    lab_panels jsonb NOT NULL,
    ordering_physician character varying(256),
    doc_path character varying(256)
);
 '   DROP TABLE public.laboratory_laborder;
       public         heap    health    false            "           1259    24337    laboratory_laborder_id_seq    SEQUENCE     �   CREATE SEQUENCE public.laboratory_laborder_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.laboratory_laborder_id_seq;
       public          health    false    291            O           0    0    laboratory_laborder_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.laboratory_laborder_id_seq OWNED BY public.laboratory_laborder.id;
          public          health    false    290            %           1259    24349    laboratory_labpanelorder    TABLE     5  CREATE TABLE public.laboratory_labpanelorder (
    id bigint NOT NULL,
    panel jsonb NOT NULL,
    status character varying(256),
    audit_log jsonb NOT NULL,
    created_at timestamp with time zone NOT NULL,
    lab_order_id bigint NOT NULL,
    patient jsonb NOT NULL,
    bill character varying(256)
);
 ,   DROP TABLE public.laboratory_labpanelorder;
       public         heap    health    false            $           1259    24348    laboratory_laborderpanel_id_seq    SEQUENCE     �   CREATE SEQUENCE public.laboratory_laborderpanel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.laboratory_laborderpanel_id_seq;
       public          health    false    293            P           0    0    laboratory_laborderpanel_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public.laboratory_laborderpanel_id_seq OWNED BY public.laboratory_labpanelorder.id;
          public          health    false    292                       1259    24322    laboratory_labpanel    TABLE       CREATE TABLE public.laboratory_labpanel (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    obv jsonb NOT NULL,
    active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    specimen_type_id bigint NOT NULL,
    lab_unit_id bigint NOT NULL,
    status character varying(256),
    audit_log jsonb,
    bill_item_code character varying(256)
);
 '   DROP TABLE public.laboratory_labpanel;
       public         heap    health    false                       1259    24321    laboratory_labpanel_id_seq    SEQUENCE     �   CREATE SEQUENCE public.laboratory_labpanel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.laboratory_labpanel_id_seq;
       public          health    false    287            Q           0    0    laboratory_labpanel_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.laboratory_labpanel_id_seq OWNED BY public.laboratory_labpanel.id;
          public          health    false    286            '           1259    24365    laboratory_labspecimen    TABLE       CREATE TABLE public.laboratory_labspecimen (
    id bigint NOT NULL,
    asn character varying(256) NOT NULL,
    type jsonb NOT NULL,
    comments jsonb,
    audit_log jsonb,
    status character varying(256) NOT NULL,
    created_at timestamp with time zone NOT NULL
);
 *   DROP TABLE public.laboratory_labspecimen;
       public         heap    health    false            &           1259    24364    laboratory_labspecimen_id_seq    SEQUENCE     �   CREATE SEQUENCE public.laboratory_labspecimen_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.laboratory_labspecimen_id_seq;
       public          health    false    295            R           0    0    laboratory_labspecimen_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.laboratory_labspecimen_id_seq OWNED BY public.laboratory_labspecimen.id;
          public          health    false    294            )           1259    24374    laboratory_labspecimentype    TABLE       CREATE TABLE public.laboratory_labspecimentype (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    color character varying(256) NOT NULL,
    description text NOT NULL,
    status boolean NOT NULL,
    created_at timestamp with time zone NOT NULL
);
 .   DROP TABLE public.laboratory_labspecimentype;
       public         heap    health    false            (           1259    24373 !   laboratory_labspecimentype_id_seq    SEQUENCE     �   CREATE SEQUENCE public.laboratory_labspecimentype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.laboratory_labspecimentype_id_seq;
       public          health    false    297            S           0    0 !   laboratory_labspecimentype_id_seq    SEQUENCE OWNED BY     g   ALTER SEQUENCE public.laboratory_labspecimentype_id_seq OWNED BY public.laboratory_labspecimentype.id;
          public          health    false    296            +           1259    24383    laboratory_labunit    TABLE     �   CREATE TABLE public.laboratory_labunit (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    order_no integer NOT NULL,
    created_at timestamp with time zone NOT NULL
);
 &   DROP TABLE public.laboratory_labunit;
       public         heap    health    false            *           1259    24382    laboratory_labunit_id_seq    SEQUENCE     �   CREATE SEQUENCE public.laboratory_labunit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.laboratory_labunit_id_seq;
       public          health    false    299            T           0    0    laboratory_labunit_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.laboratory_labunit_id_seq OWNED BY public.laboratory_labunit.id;
          public          health    false    298            !           1259    24331    laboratory_servicecenter    TABLE     �   CREATE TABLE public.laboratory_servicecenter (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp with time zone NOT NULL
);
 ,   DROP TABLE public.laboratory_servicecenter;
       public         heap    health    false                        1259    24330    laboratory_servicecenter_id_seq    SEQUENCE     �   CREATE SEQUENCE public.laboratory_servicecenter_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.laboratory_servicecenter_id_seq;
       public          health    false    289            U           0    0    laboratory_servicecenter_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public.laboratory_servicecenter_id_seq OWNED BY public.laboratory_servicecenter.id;
          public          health    false    288            -           1259    24434    patient_patient    TABLE     �  CREATE TABLE public.patient_patient (
    id bigint NOT NULL,
    is_baby boolean NOT NULL,
    salutation character varying(50),
    firstname character varying(50) NOT NULL,
    middlename character varying(50),
    lastname character varying(50) NOT NULL,
    date_of_birth date NOT NULL,
    gender character varying(50) NOT NULL,
    marital_status character varying(50),
    religion character varying(50),
    nationality character varying(50),
    state_id jsonb,
    home_address jsonb,
    next_of_kin jsonb,
    identity jsonb,
    lga character varying(255),
    phone_number character varying(15),
    payment_scheme jsonb,
    uhid character varying(50) NOT NULL,
    profile_picture text,
    email character varying(254)
);
 #   DROP TABLE public.patient_patient;
       public         heap    health    false            ,           1259    24433    patient_patient_id_seq    SEQUENCE        CREATE SEQUENCE public.patient_patient_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.patient_patient_id_seq;
       public          health    false    301            V           0    0    patient_patient_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.patient_patient_id_seq OWNED BY public.patient_patient.id;
          public          health    false    300            @           2604    23810    auth_group id    DEFAULT     n   ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);
 <   ALTER TABLE public.auth_group ALTER COLUMN id DROP DEFAULT;
       public          health    false    216    215    216            A           2604    23819    auth_group_permissions id    DEFAULT     �   ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);
 H   ALTER TABLE public.auth_group_permissions ALTER COLUMN id DROP DEFAULT;
       public          health    false    217    218    218            ?           2604    23803    auth_permission id    DEFAULT     x   ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);
 A   ALTER TABLE public.auth_permission ALTER COLUMN id DROP DEFAULT;
       public          health    false    213    214    214            B           2604    23826    auth_user id    DEFAULT     l   ALTER TABLE ONLY public.auth_user ALTER COLUMN id SET DEFAULT nextval('public.auth_user_id_seq'::regclass);
 ;   ALTER TABLE public.auth_user ALTER COLUMN id DROP DEFAULT;
       public          health    false    220    219    220            C           2604    23835    auth_user_groups id    DEFAULT     z   ALTER TABLE ONLY public.auth_user_groups ALTER COLUMN id SET DEFAULT nextval('public.auth_user_groups_id_seq'::regclass);
 B   ALTER TABLE public.auth_user_groups ALTER COLUMN id DROP DEFAULT;
       public          health    false    221    222    222            D           2604    23842    auth_user_user_permissions id    DEFAULT     �   ALTER TABLE ONLY public.auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_user_user_permissions_id_seq'::regclass);
 L   ALTER TABLE public.auth_user_user_permissions ALTER COLUMN id DROP DEFAULT;
       public          health    false    224    223    224            Q           2604    24032    constance_config id    DEFAULT     z   ALTER TABLE ONLY public.constance_config ALTER COLUMN id SET DEFAULT nextval('public.constance_config_id_seq'::regclass);
 B   ALTER TABLE public.constance_config ALTER COLUMN id DROP DEFAULT;
       public          health    false    249    248    249            G           2604    23944    core_country id    DEFAULT     r   ALTER TABLE ONLY public.core_country ALTER COLUMN id SET DEFAULT nextval('public.core_country_id_seq'::regclass);
 >   ALTER TABLE public.core_country ALTER COLUMN id DROP DEFAULT;
       public          health    false    229    228    229            O           2604    24000    core_district id    DEFAULT     t   ALTER TABLE ONLY public.core_district ALTER COLUMN id SET DEFAULT nextval('public.core_district_id_seq'::regclass);
 ?   ALTER TABLE public.core_district ALTER COLUMN id DROP DEFAULT;
       public          health    false    244    245    245            H           2604    23951    core_gender id    DEFAULT     p   ALTER TABLE ONLY public.core_gender ALTER COLUMN id SET DEFAULT nextval('public.core_gender_id_seq'::regclass);
 =   ALTER TABLE public.core_gender ALTER COLUMN id DROP DEFAULT;
       public          health    false    230    231    231            P           2604    24025    core_identity id    DEFAULT     t   ALTER TABLE ONLY public.core_identity ALTER COLUMN id SET DEFAULT nextval('public.core_identity_id_seq'::regclass);
 ?   ALTER TABLE public.core_identity ALTER COLUMN id DROP DEFAULT;
       public          health    false    246    247    247            N           2604    23993    core_lga id    DEFAULT     j   ALTER TABLE ONLY public.core_lga ALTER COLUMN id SET DEFAULT nextval('public.core_lga_id_seq'::regclass);
 :   ALTER TABLE public.core_lga ALTER COLUMN id DROP DEFAULT;
       public          health    false    242    243    243            I           2604    23958    core_maritalstatus id    DEFAULT     ~   ALTER TABLE ONLY public.core_maritalstatus ALTER COLUMN id SET DEFAULT nextval('public.core_maritalstatus_id_seq'::regclass);
 D   ALTER TABLE public.core_maritalstatus ALTER COLUMN id DROP DEFAULT;
       public          health    false    233    232    233            J           2604    23965    core_occupation id    DEFAULT     x   ALTER TABLE ONLY public.core_occupation ALTER COLUMN id SET DEFAULT nextval('public.core_occupation_id_seq'::regclass);
 A   ALTER TABLE public.core_occupation ALTER COLUMN id DROP DEFAULT;
       public          health    false    234    235    235            K           2604    23972    core_religion id    DEFAULT     t   ALTER TABLE ONLY public.core_religion ALTER COLUMN id SET DEFAULT nextval('public.core_religion_id_seq'::regclass);
 ?   ALTER TABLE public.core_religion ALTER COLUMN id DROP DEFAULT;
       public          health    false    237    236    237            L           2604    23979    core_salutation id    DEFAULT     x   ALTER TABLE ONLY public.core_salutation ALTER COLUMN id SET DEFAULT nextval('public.core_salutation_id_seq'::regclass);
 A   ALTER TABLE public.core_salutation ALTER COLUMN id DROP DEFAULT;
       public          health    false    238    239    239            M           2604    23986    core_state id    DEFAULT     n   ALTER TABLE ONLY public.core_state ALTER COLUMN id SET DEFAULT nextval('public.core_state_id_seq'::regclass);
 <   ALTER TABLE public.core_state ALTER COLUMN id DROP DEFAULT;
       public          health    false    241    240    241            E           2604    23901    django_admin_log id    DEFAULT     z   ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);
 B   ALTER TABLE public.django_admin_log ALTER COLUMN id DROP DEFAULT;
       public          health    false    225    226    226            >           2604    23794    django_content_type id    DEFAULT     �   ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);
 E   ALTER TABLE public.django_content_type ALTER COLUMN id DROP DEFAULT;
       public          health    false    212    211    212            =           2604    23785    django_migrations id    DEFAULT     |   ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);
 C   ALTER TABLE public.django_migrations ALTER COLUMN id DROP DEFAULT;
       public          health    false    209    210    210            V           2604    24083    encounters_clinic id    DEFAULT     |   ALTER TABLE ONLY public.encounters_clinic ALTER COLUMN id SET DEFAULT nextval('public.encounters_clinic_id_seq'::regclass);
 C   ALTER TABLE public.encounters_clinic ALTER COLUMN id DROP DEFAULT;
       public          health    false    259    258    259            U           2604    24074    encounters_encounter id    DEFAULT     �   ALTER TABLE ONLY public.encounters_encounter ALTER COLUMN id SET DEFAULT nextval('public.encounters_encounter_id_seq'::regclass);
 F   ALTER TABLE public.encounters_encounter ALTER COLUMN id DROP DEFAULT;
       public          health    false    256    257    257            W           2604    24114    encounters_encounter_type id    DEFAULT     �   ALTER TABLE ONLY public.encounters_encounter_type ALTER COLUMN id SET DEFAULT nextval('public.encounters_encounter_type_id_seq'::regclass);
 K   ALTER TABLE public.encounters_encounter_type ALTER COLUMN id DROP DEFAULT;
       public          health    false    261    260    261            T           2604    24065    encounters_status id    DEFAULT     |   ALTER TABLE ONLY public.encounters_status ALTER COLUMN id SET DEFAULT nextval('public.encounters_status_id_seq'::regclass);
 C   ALTER TABLE public.encounters_status ALTER COLUMN id DROP DEFAULT;
       public          health    false    254    255    255            R           2604    24044    facilities_department id    DEFAULT     �   ALTER TABLE ONLY public.facilities_department ALTER COLUMN id SET DEFAULT nextval('public.facilities_department_id_seq'::regclass);
 G   ALTER TABLE public.facilities_department ALTER COLUMN id DROP DEFAULT;
       public          health    false    250    251    251            S           2604    24053    facilities_facility id    DEFAULT     �   ALTER TABLE ONLY public.facilities_facility ALTER COLUMN id SET DEFAULT nextval('public.facilities_facility_id_seq'::regclass);
 E   ALTER TABLE public.facilities_facility ALTER COLUMN id DROP DEFAULT;
       public          health    false    252    253    253            ]           2604    24211    finance_bill id    DEFAULT     r   ALTER TABLE ONLY public.finance_bill ALTER COLUMN id SET DEFAULT nextval('public.finance_bill_id_seq'::regclass);
 >   ALTER TABLE public.finance_bill ALTER COLUMN id DROP DEFAULT;
       public          health    false    272    273    273            X           2604    24144    finance_billableitem id    DEFAULT     �   ALTER TABLE ONLY public.finance_billableitem ALTER COLUMN id SET DEFAULT nextval('public.finance_billableitem_id_seq'::regclass);
 F   ALTER TABLE public.finance_billableitem ALTER COLUMN id DROP DEFAULT;
       public          health    false    262    263    263            Y           2604    24155    finance_payer id    DEFAULT     t   ALTER TABLE ONLY public.finance_payer ALTER COLUMN id SET DEFAULT nextval('public.finance_payer_id_seq'::regclass);
 ?   ALTER TABLE public.finance_payer ALTER COLUMN id DROP DEFAULT;
       public          health    false    265    264    265            \           2604    24182    finance_payerscheme id    DEFAULT     �   ALTER TABLE ONLY public.finance_payerscheme ALTER COLUMN id SET DEFAULT nextval('public.finance_payerscheme_id_seq'::regclass);
 E   ALTER TABLE public.finance_payerscheme ALTER COLUMN id DROP DEFAULT;
       public          health    false    271    270    271            l           2604    24507    finance_payment id    DEFAULT     x   ALTER TABLE ONLY public.finance_payment ALTER COLUMN id SET DEFAULT nextval('public.finance_payment_id_seq'::regclass);
 A   ALTER TABLE public.finance_payment ALTER COLUMN id DROP DEFAULT;
       public          health    false    304    303    304            m           2604    24532    finance_paymentmethod id    DEFAULT     �   ALTER TABLE ONLY public.finance_paymentmethod ALTER COLUMN id SET DEFAULT nextval('public.finance_paymentmethod_id_seq'::regclass);
 G   ALTER TABLE public.finance_paymentmethod ALTER COLUMN id DROP DEFAULT;
       public          health    false    305    306    306            Z           2604    24164    finance_pricelist id    DEFAULT     |   ALTER TABLE ONLY public.finance_pricelist ALTER COLUMN id SET DEFAULT nextval('public.finance_pricelist_id_seq'::regclass);
 C   ALTER TABLE public.finance_pricelist ALTER COLUMN id DROP DEFAULT;
       public          health    false    266    267    267            [           2604    24173    finance_pricelistitem id    DEFAULT     �   ALTER TABLE ONLY public.finance_pricelistitem ALTER COLUMN id SET DEFAULT nextval('public.finance_pricelistitem_id_seq'::regclass);
 G   ALTER TABLE public.finance_pricelistitem ALTER COLUMN id DROP DEFAULT;
       public          health    false    268    269    269            b           2604    24271    imaging_imagingobservation id    DEFAULT     �   ALTER TABLE ONLY public.imaging_imagingobservation ALTER COLUMN id SET DEFAULT nextval('public.imaging_imagingobservation_id_seq'::regclass);
 L   ALTER TABLE public.imaging_imagingobservation ALTER COLUMN id DROP DEFAULT;
       public          health    false    283    282    283            a           2604    24262 "   imaging_imagingobservationorder id    DEFAULT     �   ALTER TABLE ONLY public.imaging_imagingobservationorder ALTER COLUMN id SET DEFAULT nextval('public.imaging_imagingobservationorder_id_seq'::regclass);
 Q   ALTER TABLE public.imaging_imagingobservationorder ALTER COLUMN id DROP DEFAULT;
       public          health    false    280    281    281            ^           2604    24237    imaging_imagingorder id    DEFAULT     �   ALTER TABLE ONLY public.imaging_imagingorder ALTER COLUMN id SET DEFAULT nextval('public.imaging_imagingorder_id_seq'::regclass);
 F   ALTER TABLE public.imaging_imagingorder ALTER COLUMN id DROP DEFAULT;
       public          health    false    274    275    275            _           2604    24248    imaging_imagingunit id    DEFAULT     |   ALTER TABLE ONLY public.imaging_imagingunit ALTER COLUMN id SET DEFAULT nextval('public.imaging_labunit_id_seq'::regclass);
 E   ALTER TABLE public.imaging_imagingunit ALTER COLUMN id DROP DEFAULT;
       public          health    false    277    276    277            `           2604    24255    imaging_servicecenter id    DEFAULT     �   ALTER TABLE ONLY public.imaging_servicecenter ALTER COLUMN id SET DEFAULT nextval('public.imaging_servicecenter_id_seq'::regclass);
 G   ALTER TABLE public.imaging_servicecenter ALTER COLUMN id DROP DEFAULT;
       public          health    false    278    279    279            c           2604    24316    laboratory_labobservation id    DEFAULT     �   ALTER TABLE ONLY public.laboratory_labobservation ALTER COLUMN id SET DEFAULT nextval('public.laboratory_labobservation_id_seq'::regclass);
 K   ALTER TABLE public.laboratory_labobservation ALTER COLUMN id DROP DEFAULT;
       public          health    false    285    284    285            f           2604    24341    laboratory_laborder id    DEFAULT     �   ALTER TABLE ONLY public.laboratory_laborder ALTER COLUMN id SET DEFAULT nextval('public.laboratory_laborder_id_seq'::regclass);
 E   ALTER TABLE public.laboratory_laborder ALTER COLUMN id DROP DEFAULT;
       public          health    false    290    291    291            d           2604    24325    laboratory_labpanel id    DEFAULT     �   ALTER TABLE ONLY public.laboratory_labpanel ALTER COLUMN id SET DEFAULT nextval('public.laboratory_labpanel_id_seq'::regclass);
 E   ALTER TABLE public.laboratory_labpanel ALTER COLUMN id DROP DEFAULT;
       public          health    false    286    287    287            g           2604    24352    laboratory_labpanelorder id    DEFAULT     �   ALTER TABLE ONLY public.laboratory_labpanelorder ALTER COLUMN id SET DEFAULT nextval('public.laboratory_laborderpanel_id_seq'::regclass);
 J   ALTER TABLE public.laboratory_labpanelorder ALTER COLUMN id DROP DEFAULT;
       public          health    false    293    292    293            h           2604    24368    laboratory_labspecimen id    DEFAULT     �   ALTER TABLE ONLY public.laboratory_labspecimen ALTER COLUMN id SET DEFAULT nextval('public.laboratory_labspecimen_id_seq'::regclass);
 H   ALTER TABLE public.laboratory_labspecimen ALTER COLUMN id DROP DEFAULT;
       public          health    false    295    294    295            i           2604    24377    laboratory_labspecimentype id    DEFAULT     �   ALTER TABLE ONLY public.laboratory_labspecimentype ALTER COLUMN id SET DEFAULT nextval('public.laboratory_labspecimentype_id_seq'::regclass);
 L   ALTER TABLE public.laboratory_labspecimentype ALTER COLUMN id DROP DEFAULT;
       public          health    false    297    296    297            j           2604    24386    laboratory_labunit id    DEFAULT     ~   ALTER TABLE ONLY public.laboratory_labunit ALTER COLUMN id SET DEFAULT nextval('public.laboratory_labunit_id_seq'::regclass);
 D   ALTER TABLE public.laboratory_labunit ALTER COLUMN id DROP DEFAULT;
       public          health    false    298    299    299            e           2604    24334    laboratory_servicecenter id    DEFAULT     �   ALTER TABLE ONLY public.laboratory_servicecenter ALTER COLUMN id SET DEFAULT nextval('public.laboratory_servicecenter_id_seq'::regclass);
 J   ALTER TABLE public.laboratory_servicecenter ALTER COLUMN id DROP DEFAULT;
       public          health    false    288    289    289            k           2604    24437    patient_patient id    DEFAULT     x   ALTER TABLE ONLY public.patient_patient ALTER COLUMN id SET DEFAULT nextval('public.patient_patient_id_seq'::regclass);
 A   ALTER TABLE public.patient_patient ALTER COLUMN id DROP DEFAULT;
       public          health    false    300    301    301            �          0    23807 
   auth_group 
   TABLE DATA           .   COPY public.auth_group (id, name) FROM stdin;
    public          health    false    216   �,      �          0    23816    auth_group_permissions 
   TABLE DATA           M   COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
    public          health    false    218   -      �          0    23800    auth_permission 
   TABLE DATA           N   COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
    public          health    false    214   3-      �          0    23823 	   auth_user 
   TABLE DATA           �   COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
    public          health    false    220   C4      �          0    23832    auth_user_groups 
   TABLE DATA           A   COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
    public          health    false    222   �4      �          0    23839    auth_user_user_permissions 
   TABLE DATA           P   COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
    public          health    false    224   5      �          0    23927    authtoken_token 
   TABLE DATA           @   COPY public.authtoken_token (key, created, user_id) FROM stdin;
    public          health    false    227   45      �          0    24029    constance_config 
   TABLE DATA           :   COPY public.constance_config (id, key, value) FROM stdin;
    public          health    false    249   �5      �          0    23941    core_country 
   TABLE DATA           3   COPY public.core_country (id, country) FROM stdin;
    public          health    false    229   7      �          0    23997    core_district 
   TABLE DATA           ?   COPY public.core_district (id, district, state_id) FROM stdin;
    public          health    false    245   (7      �          0    23948    core_gender 
   TABLE DATA           1   COPY public.core_gender (id, gender) FROM stdin;
    public          health    false    231   E7      �          0    24022    core_identity 
   TABLE DATA           1   COPY public.core_identity (id, name) FROM stdin;
    public          health    false    247   b7      �          0    23990    core_lga 
   TABLE DATA           5   COPY public.core_lga (id, lga, state_id) FROM stdin;
    public          health    false    243   7      �          0    23955    core_maritalstatus 
   TABLE DATA           @   COPY public.core_maritalstatus (id, marital_status) FROM stdin;
    public          health    false    233   �7      �          0    23962    core_occupation 
   TABLE DATA           9   COPY public.core_occupation (id, occupation) FROM stdin;
    public          health    false    235   �7      �          0    23969    core_religion 
   TABLE DATA           5   COPY public.core_religion (id, religion) FROM stdin;
    public          health    false    237   �7      �          0    23976    core_salutation 
   TABLE DATA           :   COPY public.core_salutation (id, salutations) FROM stdin;
    public          health    false    239   �7      �          0    23983 
   core_state 
   TABLE DATA           ;   COPY public.core_state (id, state, country_id) FROM stdin;
    public          health    false    241   8      �          0    23898    django_admin_log 
   TABLE DATA           �   COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
    public          health    false    226   -8      �          0    23791    django_content_type 
   TABLE DATA           C   COPY public.django_content_type (id, app_label, model) FROM stdin;
    public          health    false    212   J8      �          0    23782    django_migrations 
   TABLE DATA           C   COPY public.django_migrations (id, app, name, applied) FROM stdin;
    public          health    false    210   �9                0    24451    django_session 
   TABLE DATA           P   COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
    public          health    false    302   �A      �          0    24080    encounters_clinic 
   TABLE DATA           a   COPY public.encounters_clinic (id, name, is_active, "Department_id", bill_item_code) FROM stdin;
    public          health    false    259   C      �          0    24071    encounters_encounter 
   TABLE DATA           �   COPY public.encounters_encounter (id, encounter_id, clinic, time_log, chart, provider, patient, is_active, status, encounter_type, encounter_datetime, created_datetime, chief_complaint, bill, signed_date) FROM stdin;
    public          health    false    257   (C      �          0    24111    encounters_encounter_type 
   TABLE DATA           =   COPY public.encounters_encounter_type (id, name) FROM stdin;
    public          health    false    261   EC      �          0    24062    encounters_status 
   TABLE DATA           5   COPY public.encounters_status (id, name) FROM stdin;
    public          health    false    255   bC      �          0    24041    facilities_department 
   TABLE DATA           _   COPY public.facilities_department (id, name, description, display_name, is_active) FROM stdin;
    public          health    false    251   C      �          0    24050    facilities_facility 
   TABLE DATA           z   COPY public.facilities_facility (id, name, address, state, city, lga, phone, email, facility_code, is_active) FROM stdin;
    public          health    false    253   �C      �          0    24208    finance_bill 
   TABLE DATA             COPY public.finance_bill (id, bill_item_code, cost_price, selling_price, cleared_status, quantity, bill_source, billed_to_type, service_center, description, is_service_rendered, is_invoiced, transaction_date, billed_to_id, co_pay, auth_code, is_capitated, patient) FROM stdin;
    public          health    false    273   �C      �          0    24141    finance_billableitem 
   TABLE DATA           �   COPY public.finance_billableitem (id, item_code, description, cost, selling_price, module, created_at, updated_at, created_by, updated_by) FROM stdin;
    public          health    false    263   �C      �          0    24152    finance_payer 
   TABLE DATA           R   COPY public.finance_payer (id, name, address, created_at, updated_at) FROM stdin;
    public          health    false    265   �W      �          0    24179    finance_payerscheme 
   TABLE DATA           �   COPY public.finance_payerscheme (id, name, created_by, created_at, updated_by, updated_at, payer_id, price_list_id, type) FROM stdin;
    public          health    false    271   �W                0    24504    finance_payment 
   TABLE DATA           u   COPY public.finance_payment (id, bills, patient, total_amount, audit_log, created_at, payment_method_id) FROM stdin;
    public          health    false    304   �W                 0    24529    finance_paymentmethod 
   TABLE DATA           ^   COPY public.finance_paymentmethod (id, name, description, created_at, updated_at) FROM stdin;
    public          health    false    306   �W      �          0    24161    finance_pricelist 
   TABLE DATA           x   COPY public.finance_pricelist (id, name, description, created_by, created_at, updated_by, updated_at, meta) FROM stdin;
    public          health    false    267   X      �          0    24170    finance_pricelistitem 
   TABLE DATA           �   COPY public.finance_pricelistitem (id, bill_item_code, selling_price, co_pay, is_auth_req, is_capitated, created_by, created_at, updated_by, updated_at, price_list_id) FROM stdin;
    public          health    false    269   X      	          0    24268    imaging_imagingobservation 
   TABLE DATA           �   COPY public.imaging_imagingobservation (id, name, active, status, audit_log, created_at, img_unit_id, bill_item_code) FROM stdin;
    public          health    false    283   <X                0    24259    imaging_imagingobservationorder 
   TABLE DATA           �   COPY public.imaging_imagingobservationorder (id, img_obv, status, audit_log, created_at, img_order_id, patient, bill) FROM stdin;
    public          health    false    281   �]                0    24234    imaging_imagingorder 
   TABLE DATA           �   COPY public.imaging_imagingorder (id, patient, img_id, stat, service_center, referral_facility, comments, img_obv, img_obv_orders, ordered_by, ordered_datetime, ordering_physician) FROM stdin;
    public          health    false    275   �]                0    24245    imaging_imagingunit 
   TABLE DATA           M   COPY public.imaging_imagingunit (id, name, order_no, created_at) FROM stdin;
    public          health    false    277   �]                0    24252    imaging_servicecenter 
   TABLE DATA           E   COPY public.imaging_servicecenter (id, name, created_at) FROM stdin;
    public          health    false    279   B^                0    24313    laboratory_labobservation 
   TABLE DATA           e   COPY public.laboratory_labobservation (id, name, uom, reference_range, type, created_at) FROM stdin;
    public          health    false    285   _^                0    24338    laboratory_laborder 
   TABLE DATA           �   COPY public.laboratory_laborder (id, patient, asn, stat, service_center, referral_facility, comments, ordered_by, ordered_datetime, lab_panel_orders, lab_panels, ordering_physician, doc_path) FROM stdin;
    public          health    false    291   �^                0    24322    laboratory_labpanel 
   TABLE DATA           �   COPY public.laboratory_labpanel (id, name, obv, active, created_at, specimen_type_id, lab_unit_id, status, audit_log, bill_item_code) FROM stdin;
    public          health    false    287   �^                0    24349    laboratory_labpanelorder 
   TABLE DATA           y   COPY public.laboratory_labpanelorder (id, panel, status, audit_log, created_at, lab_order_id, patient, bill) FROM stdin;
    public          health    false    293   -q                0    24365    laboratory_labspecimen 
   TABLE DATA           h   COPY public.laboratory_labspecimen (id, asn, type, comments, audit_log, status, created_at) FROM stdin;
    public          health    false    295   Jq                0    24374    laboratory_labspecimentype 
   TABLE DATA           f   COPY public.laboratory_labspecimentype (id, name, color, description, status, created_at) FROM stdin;
    public          health    false    297   gq                0    24383    laboratory_labunit 
   TABLE DATA           L   COPY public.laboratory_labunit (id, name, order_no, created_at) FROM stdin;
    public          health    false    299   �s                0    24331    laboratory_servicecenter 
   TABLE DATA           H   COPY public.laboratory_servicecenter (id, name, created_at) FROM stdin;
    public          health    false    289   t                0    24434    patient_patient 
   TABLE DATA             COPY public.patient_patient (id, is_baby, salutation, firstname, middlename, lastname, date_of_birth, gender, marital_status, religion, nationality, state_id, home_address, next_of_kin, identity, lga, phone_number, payment_scheme, uhid, profile_picture, email) FROM stdin;
    public          health    false    301   !t      W           0    0    auth_group_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);
          public          health    false    215            X           0    0    auth_group_permissions_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);
          public          health    false    217            Y           0    0    auth_permission_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.auth_permission_id_seq', 206, true);
          public          health    false    213            Z           0    0    auth_user_groups_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);
          public          health    false    221            [           0    0    auth_user_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.auth_user_id_seq', 33, true);
          public          health    false    219            \           0    0 !   auth_user_user_permissions_id_seq    SEQUENCE SET     P   SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);
          public          health    false    223            ]           0    0    constance_config_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.constance_config_id_seq', 33, true);
          public          health    false    248            ^           0    0    core_country_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.core_country_id_seq', 1, false);
          public          health    false    228            _           0    0    core_district_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.core_district_id_seq', 1, false);
          public          health    false    244            `           0    0    core_gender_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.core_gender_id_seq', 1, false);
          public          health    false    230            a           0    0    core_identity_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.core_identity_id_seq', 1, false);
          public          health    false    246            b           0    0    core_lga_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.core_lga_id_seq', 1, false);
          public          health    false    242            c           0    0    core_maritalstatus_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.core_maritalstatus_id_seq', 1, false);
          public          health    false    232            d           0    0    core_occupation_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.core_occupation_id_seq', 1, false);
          public          health    false    234            e           0    0    core_religion_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.core_religion_id_seq', 1, false);
          public          health    false    236            f           0    0    core_salutation_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.core_salutation_id_seq', 1, false);
          public          health    false    238            g           0    0    core_state_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.core_state_id_seq', 1, false);
          public          health    false    240            h           0    0    django_admin_log_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);
          public          health    false    225            i           0    0    django_content_type_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.django_content_type_id_seq', 68, true);
          public          health    false    211            j           0    0    django_migrations_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.django_migrations_id_seq', 107, true);
          public          health    false    209            k           0    0    encounters_clinic_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.encounters_clinic_id_seq', 1, false);
          public          health    false    258            l           0    0    encounters_encounter_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.encounters_encounter_id_seq', 1, false);
          public          health    false    256            m           0    0     encounters_encounter_type_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.encounters_encounter_type_id_seq', 1, false);
          public          health    false    260            n           0    0    encounters_status_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.encounters_status_id_seq', 1, false);
          public          health    false    254            o           0    0    facilities_department_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.facilities_department_id_seq', 1, false);
          public          health    false    250            p           0    0    facilities_facility_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.facilities_facility_id_seq', 1, false);
          public          health    false    252            q           0    0    finance_bill_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.finance_bill_id_seq', 1, false);
          public          health    false    272            r           0    0    finance_billableitem_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.finance_billableitem_id_seq', 292, true);
          public          health    false    262            s           0    0    finance_payer_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.finance_payer_id_seq', 1, false);
          public          health    false    264            t           0    0    finance_payerscheme_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.finance_payerscheme_id_seq', 1, false);
          public          health    false    270            u           0    0    finance_payment_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.finance_payment_id_seq', 1, false);
          public          health    false    303            v           0    0    finance_paymentmethod_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.finance_paymentmethod_id_seq', 1, false);
          public          health    false    305            w           0    0    finance_pricelist_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.finance_pricelist_id_seq', 1, false);
          public          health    false    266            x           0    0    finance_pricelistitem_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.finance_pricelistitem_id_seq', 1, false);
          public          health    false    268            y           0    0 !   imaging_imagingobservation_id_seq    SEQUENCE SET     P   SELECT pg_catalog.setval('public.imaging_imagingobservation_id_seq', 59, true);
          public          health    false    282            z           0    0 &   imaging_imagingobservationorder_id_seq    SEQUENCE SET     U   SELECT pg_catalog.setval('public.imaging_imagingobservationorder_id_seq', 1, false);
          public          health    false    280            {           0    0    imaging_imagingorder_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.imaging_imagingorder_id_seq', 1, false);
          public          health    false    274            |           0    0    imaging_labunit_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.imaging_labunit_id_seq', 1, true);
          public          health    false    276            }           0    0    imaging_servicecenter_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.imaging_servicecenter_id_seq', 1, false);
          public          health    false    278            ~           0    0     laboratory_labobservation_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.laboratory_labobservation_id_seq', 33, true);
          public          health    false    284                       0    0    laboratory_laborder_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.laboratory_laborder_id_seq', 1, false);
          public          health    false    290            �           0    0    laboratory_laborderpanel_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.laboratory_laborderpanel_id_seq', 1, false);
          public          health    false    292            �           0    0    laboratory_labpanel_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.laboratory_labpanel_id_seq', 231, true);
          public          health    false    286            �           0    0    laboratory_labspecimen_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.laboratory_labspecimen_id_seq', 1, false);
          public          health    false    294            �           0    0 !   laboratory_labspecimentype_id_seq    SEQUENCE SET     P   SELECT pg_catalog.setval('public.laboratory_labspecimentype_id_seq', 60, true);
          public          health    false    296            �           0    0    laboratory_labunit_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.laboratory_labunit_id_seq', 33, true);
          public          health    false    298            �           0    0    laboratory_servicecenter_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.laboratory_servicecenter_id_seq', 1, false);
          public          health    false    288            �           0    0    patient_patient_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.patient_patient_id_seq', 1, false);
          public          health    false    300            {           2606    23925    auth_group auth_group_name_key 
   CONSTRAINT     Y   ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);
 H   ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_name_key;
       public            health    false    216            �           2606    23855 R   auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);
 |   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
       public            health    false    218    218            �           2606    23821 2   auth_group_permissions auth_group_permissions_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_pkey;
       public            health    false    218            }           2606    23812    auth_group auth_group_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_pkey;
       public            health    false    216            v           2606    23846 F   auth_permission auth_permission_content_type_id_codename_01ab375a_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);
 p   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq;
       public            health    false    214    214            x           2606    23805 $   auth_permission auth_permission_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_pkey;
       public            health    false    214            �           2606    23837 &   auth_user_groups auth_user_groups_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_pkey;
       public            health    false    222            �           2606    23870 @   auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);
 j   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq;
       public            health    false    222    222            �           2606    23828    auth_user auth_user_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.auth_user DROP CONSTRAINT auth_user_pkey;
       public            health    false    220            �           2606    23844 :   auth_user_user_permissions auth_user_user_permissions_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_pkey;
       public            health    false    224            �           2606    23884 Y   auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);
 �   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq;
       public            health    false    224    224            �           2606    23920     auth_user auth_user_username_key 
   CONSTRAINT     _   ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);
 J   ALTER TABLE ONLY public.auth_user DROP CONSTRAINT auth_user_username_key;
       public            health    false    220            �           2606    23931 $   authtoken_token authtoken_token_pkey 
   CONSTRAINT     c   ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_pkey PRIMARY KEY (key);
 N   ALTER TABLE ONLY public.authtoken_token DROP CONSTRAINT authtoken_token_pkey;
       public            health    false    227            �           2606    23933 +   authtoken_token authtoken_token_user_id_key 
   CONSTRAINT     i   ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_key UNIQUE (user_id);
 U   ALTER TABLE ONLY public.authtoken_token DROP CONSTRAINT authtoken_token_user_id_key;
       public            health    false    227            �           2606    24038 )   constance_config constance_config_key_key 
   CONSTRAINT     c   ALTER TABLE ONLY public.constance_config
    ADD CONSTRAINT constance_config_key_key UNIQUE (key);
 S   ALTER TABLE ONLY public.constance_config DROP CONSTRAINT constance_config_key_key;
       public            health    false    249            �           2606    24036 &   constance_config constance_config_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.constance_config
    ADD CONSTRAINT constance_config_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.constance_config DROP CONSTRAINT constance_config_pkey;
       public            health    false    249            �           2606    23946    core_country core_country_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.core_country
    ADD CONSTRAINT core_country_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.core_country DROP CONSTRAINT core_country_pkey;
       public            health    false    229            �           2606    24002     core_district core_district_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.core_district
    ADD CONSTRAINT core_district_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.core_district DROP CONSTRAINT core_district_pkey;
       public            health    false    245            �           2606    23953    core_gender core_gender_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.core_gender
    ADD CONSTRAINT core_gender_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.core_gender DROP CONSTRAINT core_gender_pkey;
       public            health    false    231            �           2606    24027     core_identity core_identity_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.core_identity
    ADD CONSTRAINT core_identity_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.core_identity DROP CONSTRAINT core_identity_pkey;
       public            health    false    247            �           2606    23995    core_lga core_lga_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.core_lga
    ADD CONSTRAINT core_lga_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.core_lga DROP CONSTRAINT core_lga_pkey;
       public            health    false    243            �           2606    23960 *   core_maritalstatus core_maritalstatus_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.core_maritalstatus
    ADD CONSTRAINT core_maritalstatus_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.core_maritalstatus DROP CONSTRAINT core_maritalstatus_pkey;
       public            health    false    233            �           2606    23967 $   core_occupation core_occupation_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.core_occupation
    ADD CONSTRAINT core_occupation_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.core_occupation DROP CONSTRAINT core_occupation_pkey;
       public            health    false    235            �           2606    23974     core_religion core_religion_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.core_religion
    ADD CONSTRAINT core_religion_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.core_religion DROP CONSTRAINT core_religion_pkey;
       public            health    false    237            �           2606    23981 $   core_salutation core_salutation_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.core_salutation
    ADD CONSTRAINT core_salutation_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.core_salutation DROP CONSTRAINT core_salutation_pkey;
       public            health    false    239            �           2606    23988    core_state core_state_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.core_state
    ADD CONSTRAINT core_state_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.core_state DROP CONSTRAINT core_state_pkey;
       public            health    false    241            �           2606    23906 &   django_admin_log django_admin_log_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_pkey;
       public            health    false    226            q           2606    23798 E   django_content_type django_content_type_app_label_model_76bd3d3b_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);
 o   ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq;
       public            health    false    212    212            s           2606    23796 ,   django_content_type django_content_type_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_pkey;
       public            health    false    212            o           2606    23789 (   django_migrations django_migrations_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.django_migrations DROP CONSTRAINT django_migrations_pkey;
       public            health    false    210                       2606    24457 "   django_session django_session_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);
 L   ALTER TABLE ONLY public.django_session DROP CONSTRAINT django_session_pkey;
       public            health    false    302            �           2606    24087 ,   encounters_clinic encounters_clinic_name_key 
   CONSTRAINT     g   ALTER TABLE ONLY public.encounters_clinic
    ADD CONSTRAINT encounters_clinic_name_key UNIQUE (name);
 V   ALTER TABLE ONLY public.encounters_clinic DROP CONSTRAINT encounters_clinic_name_key;
       public            health    false    259            �           2606    24085 (   encounters_clinic encounters_clinic_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.encounters_clinic
    ADD CONSTRAINT encounters_clinic_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.encounters_clinic DROP CONSTRAINT encounters_clinic_pkey;
       public            health    false    259            �           2606    24108 D   encounters_encounter encounters_encounter_encounter_id_acc9683d_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.encounters_encounter
    ADD CONSTRAINT encounters_encounter_encounter_id_acc9683d_uniq UNIQUE (encounter_id);
 n   ALTER TABLE ONLY public.encounters_encounter DROP CONSTRAINT encounters_encounter_encounter_id_acc9683d_uniq;
       public            health    false    257            �           2606    24078 .   encounters_encounter encounters_encounter_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.encounters_encounter
    ADD CONSTRAINT encounters_encounter_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.encounters_encounter DROP CONSTRAINT encounters_encounter_pkey;
       public            health    false    257            �           2606    24118 <   encounters_encounter_type encounters_encounter_type_name_key 
   CONSTRAINT     w   ALTER TABLE ONLY public.encounters_encounter_type
    ADD CONSTRAINT encounters_encounter_type_name_key UNIQUE (name);
 f   ALTER TABLE ONLY public.encounters_encounter_type DROP CONSTRAINT encounters_encounter_type_name_key;
       public            health    false    261            �           2606    24116 8   encounters_encounter_type encounters_encounter_type_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.encounters_encounter_type
    ADD CONSTRAINT encounters_encounter_type_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.encounters_encounter_type DROP CONSTRAINT encounters_encounter_type_pkey;
       public            health    false    261            �           2606    24067 (   encounters_status encounters_status_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.encounters_status
    ADD CONSTRAINT encounters_status_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.encounters_status DROP CONSTRAINT encounters_status_pkey;
       public            health    false    255            �           2606    24069 .   encounters_status encounters_status_status_key 
   CONSTRAINT     i   ALTER TABLE ONLY public.encounters_status
    ADD CONSTRAINT encounters_status_status_key UNIQUE (name);
 X   ALTER TABLE ONLY public.encounters_status DROP CONSTRAINT encounters_status_status_key;
       public            health    false    255            �           2606    24048 0   facilities_department facilities_department_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.facilities_department
    ADD CONSTRAINT facilities_department_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.facilities_department DROP CONSTRAINT facilities_department_pkey;
       public            health    false    251            �           2606    24059 0   facilities_facility facilities_facility_name_key 
   CONSTRAINT     k   ALTER TABLE ONLY public.facilities_facility
    ADD CONSTRAINT facilities_facility_name_key UNIQUE (name);
 Z   ALTER TABLE ONLY public.facilities_facility DROP CONSTRAINT facilities_facility_name_key;
       public            health    false    253            �           2606    24057 ,   facilities_facility facilities_facility_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.facilities_facility
    ADD CONSTRAINT facilities_facility_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.facilities_facility DROP CONSTRAINT facilities_facility_pkey;
       public            health    false    253            �           2606    24215    finance_bill finance_bill_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.finance_bill
    ADD CONSTRAINT finance_bill_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.finance_bill DROP CONSTRAINT finance_bill_pkey;
       public            health    false    273            �           2606    24150 7   finance_billableitem finance_billableitem_item_code_key 
   CONSTRAINT     w   ALTER TABLE ONLY public.finance_billableitem
    ADD CONSTRAINT finance_billableitem_item_code_key UNIQUE (item_code);
 a   ALTER TABLE ONLY public.finance_billableitem DROP CONSTRAINT finance_billableitem_item_code_key;
       public            health    false    263            �           2606    24148 .   finance_billableitem finance_billableitem_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.finance_billableitem
    ADD CONSTRAINT finance_billableitem_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.finance_billableitem DROP CONSTRAINT finance_billableitem_pkey;
       public            health    false    263            �           2606    24159     finance_payer finance_payer_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.finance_payer
    ADD CONSTRAINT finance_payer_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.finance_payer DROP CONSTRAINT finance_payer_pkey;
       public            health    false    265            �           2606    24186 ,   finance_payerscheme finance_payerscheme_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.finance_payerscheme
    ADD CONSTRAINT finance_payerscheme_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.finance_payerscheme DROP CONSTRAINT finance_payerscheme_pkey;
       public            health    false    271                       2606    24511 $   finance_payment finance_payment_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.finance_payment
    ADD CONSTRAINT finance_payment_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.finance_payment DROP CONSTRAINT finance_payment_pkey;
       public            health    false    304                       2606    24536 0   finance_paymentmethod finance_paymentmethod_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.finance_paymentmethod
    ADD CONSTRAINT finance_paymentmethod_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.finance_paymentmethod DROP CONSTRAINT finance_paymentmethod_pkey;
       public            health    false    306            �           2606    24168 (   finance_pricelist finance_pricelist_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.finance_pricelist
    ADD CONSTRAINT finance_pricelist_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.finance_pricelist DROP CONSTRAINT finance_pricelist_pkey;
       public            health    false    267            �           2606    24177 0   finance_pricelistitem finance_pricelistitem_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.finance_pricelistitem
    ADD CONSTRAINT finance_pricelistitem_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.finance_pricelistitem DROP CONSTRAINT finance_pricelistitem_pkey;
       public            health    false    269            �           2606    24275 :   imaging_imagingobservation imaging_imagingobservation_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.imaging_imagingobservation
    ADD CONSTRAINT imaging_imagingobservation_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.imaging_imagingobservation DROP CONSTRAINT imaging_imagingobservation_pkey;
       public            health    false    283            �           2606    24266 D   imaging_imagingobservationorder imaging_imagingobservationorder_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.imaging_imagingobservationorder
    ADD CONSTRAINT imaging_imagingobservationorder_pkey PRIMARY KEY (id);
 n   ALTER TABLE ONLY public.imaging_imagingobservationorder DROP CONSTRAINT imaging_imagingobservationorder_pkey;
       public            health    false    281            �           2606    24243 4   imaging_imagingorder imaging_imagingorder_img_id_key 
   CONSTRAINT     q   ALTER TABLE ONLY public.imaging_imagingorder
    ADD CONSTRAINT imaging_imagingorder_img_id_key UNIQUE (img_id);
 ^   ALTER TABLE ONLY public.imaging_imagingorder DROP CONSTRAINT imaging_imagingorder_img_id_key;
       public            health    false    275            �           2606    24241 .   imaging_imagingorder imaging_imagingorder_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.imaging_imagingorder
    ADD CONSTRAINT imaging_imagingorder_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.imaging_imagingorder DROP CONSTRAINT imaging_imagingorder_pkey;
       public            health    false    275            �           2606    24250 (   imaging_imagingunit imaging_labunit_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.imaging_imagingunit
    ADD CONSTRAINT imaging_labunit_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.imaging_imagingunit DROP CONSTRAINT imaging_labunit_pkey;
       public            health    false    277            �           2606    24257 0   imaging_servicecenter imaging_servicecenter_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.imaging_servicecenter
    ADD CONSTRAINT imaging_servicecenter_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.imaging_servicecenter DROP CONSTRAINT imaging_servicecenter_pkey;
       public            health    false    279            �           2606    24320 8   laboratory_labobservation laboratory_labobservation_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.laboratory_labobservation
    ADD CONSTRAINT laboratory_labobservation_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.laboratory_labobservation DROP CONSTRAINT laboratory_labobservation_pkey;
       public            health    false    285                       2606    24347 /   laboratory_laborder laboratory_laborder_asn_key 
   CONSTRAINT     i   ALTER TABLE ONLY public.laboratory_laborder
    ADD CONSTRAINT laboratory_laborder_asn_key UNIQUE (asn);
 Y   ALTER TABLE ONLY public.laboratory_laborder DROP CONSTRAINT laboratory_laborder_asn_key;
       public            health    false    291                       2606    24345 ,   laboratory_laborder laboratory_laborder_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.laboratory_laborder
    ADD CONSTRAINT laboratory_laborder_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.laboratory_laborder DROP CONSTRAINT laboratory_laborder_pkey;
       public            health    false    291                       2606    24356 6   laboratory_labpanelorder laboratory_laborderpanel_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.laboratory_labpanelorder
    ADD CONSTRAINT laboratory_laborderpanel_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.laboratory_labpanelorder DROP CONSTRAINT laboratory_laborderpanel_pkey;
       public            health    false    293            �           2606    24329 ,   laboratory_labpanel laboratory_labpanel_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.laboratory_labpanel
    ADD CONSTRAINT laboratory_labpanel_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.laboratory_labpanel DROP CONSTRAINT laboratory_labpanel_pkey;
       public            health    false    287            	           2606    24372 2   laboratory_labspecimen laboratory_labspecimen_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.laboratory_labspecimen
    ADD CONSTRAINT laboratory_labspecimen_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.laboratory_labspecimen DROP CONSTRAINT laboratory_labspecimen_pkey;
       public            health    false    295                       2606    24381 :   laboratory_labspecimentype laboratory_labspecimentype_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.laboratory_labspecimentype
    ADD CONSTRAINT laboratory_labspecimentype_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.laboratory_labspecimentype DROP CONSTRAINT laboratory_labspecimentype_pkey;
       public            health    false    297                       2606    24388 *   laboratory_labunit laboratory_labunit_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.laboratory_labunit
    ADD CONSTRAINT laboratory_labunit_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.laboratory_labunit DROP CONSTRAINT laboratory_labunit_pkey;
       public            health    false    299            �           2606    24336 6   laboratory_servicecenter laboratory_servicecenter_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.laboratory_servicecenter
    ADD CONSTRAINT laboratory_servicecenter_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.laboratory_servicecenter DROP CONSTRAINT laboratory_servicecenter_pkey;
       public            health    false    289                       2606    24441 $   patient_patient patient_patient_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.patient_patient
    ADD CONSTRAINT patient_patient_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.patient_patient DROP CONSTRAINT patient_patient_pkey;
       public            health    false    301                       2606    24448 2   patient_patient patient_patient_uhid_8d67a08a_uniq 
   CONSTRAINT     m   ALTER TABLE ONLY public.patient_patient
    ADD CONSTRAINT patient_patient_uhid_8d67a08a_uniq UNIQUE (uhid);
 \   ALTER TABLE ONLY public.patient_patient DROP CONSTRAINT patient_patient_uhid_8d67a08a_uniq;
       public            health    false    301            y           1259    23926    auth_group_name_a6ea08ec_like    INDEX     h   CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);
 1   DROP INDEX public.auth_group_name_a6ea08ec_like;
       public            health    false    216            ~           1259    23866 (   auth_group_permissions_group_id_b120cbf9    INDEX     o   CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);
 <   DROP INDEX public.auth_group_permissions_group_id_b120cbf9;
       public            health    false    218            �           1259    23867 -   auth_group_permissions_permission_id_84c5c92e    INDEX     y   CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);
 A   DROP INDEX public.auth_group_permissions_permission_id_84c5c92e;
       public            health    false    218            t           1259    23852 (   auth_permission_content_type_id_2f476e4b    INDEX     o   CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);
 <   DROP INDEX public.auth_permission_content_type_id_2f476e4b;
       public            health    false    214            �           1259    23882 "   auth_user_groups_group_id_97559544    INDEX     c   CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);
 6   DROP INDEX public.auth_user_groups_group_id_97559544;
       public            health    false    222            �           1259    23881 !   auth_user_groups_user_id_6a12ed8b    INDEX     a   CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);
 5   DROP INDEX public.auth_user_groups_user_id_6a12ed8b;
       public            health    false    222            �           1259    23896 1   auth_user_user_permissions_permission_id_1fbb5f2c    INDEX     �   CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);
 E   DROP INDEX public.auth_user_user_permissions_permission_id_1fbb5f2c;
       public            health    false    224            �           1259    23895 +   auth_user_user_permissions_user_id_a95ead1b    INDEX     u   CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);
 ?   DROP INDEX public.auth_user_user_permissions_user_id_a95ead1b;
       public            health    false    224            �           1259    23921     auth_user_username_6821ab7c_like    INDEX     n   CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);
 4   DROP INDEX public.auth_user_username_6821ab7c_like;
       public            health    false    220            �           1259    23939 !   authtoken_token_key_10f0b77e_like    INDEX     p   CREATE INDEX authtoken_token_key_10f0b77e_like ON public.authtoken_token USING btree (key varchar_pattern_ops);
 5   DROP INDEX public.authtoken_token_key_10f0b77e_like;
       public            health    false    227            �           1259    24039 "   constance_config_key_baef3136_like    INDEX     r   CREATE INDEX constance_config_key_baef3136_like ON public.constance_config USING btree (key varchar_pattern_ops);
 6   DROP INDEX public.constance_config_key_baef3136_like;
       public            health    false    249            �           1259    24020    core_district_state_id_ff1e236a    INDEX     ]   CREATE INDEX core_district_state_id_ff1e236a ON public.core_district USING btree (state_id);
 3   DROP INDEX public.core_district_state_id_ff1e236a;
       public            health    false    245            �           1259    24014    core_lga_state_id_9bdeff3f    INDEX     S   CREATE INDEX core_lga_state_id_9bdeff3f ON public.core_lga USING btree (state_id);
 .   DROP INDEX public.core_lga_state_id_9bdeff3f;
       public            health    false    243            �           1259    24008    core_state_country_id_5a16f697    INDEX     [   CREATE INDEX core_state_country_id_5a16f697 ON public.core_state USING btree (country_id);
 2   DROP INDEX public.core_state_country_id_5a16f697;
       public            health    false    241            �           1259    23917 )   django_admin_log_content_type_id_c4bce8eb    INDEX     q   CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);
 =   DROP INDEX public.django_admin_log_content_type_id_c4bce8eb;
       public            health    false    226            �           1259    23918 !   django_admin_log_user_id_c564eba6    INDEX     a   CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);
 5   DROP INDEX public.django_admin_log_user_id_c564eba6;
       public            health    false    226                       1259    24459 #   django_session_expire_date_a5c62663    INDEX     e   CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);
 7   DROP INDEX public.django_session_expire_date_a5c62663;
       public            health    false    302                       1259    24458 (   django_session_session_key_c0390e0f_like    INDEX     ~   CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);
 <   DROP INDEX public.django_session_session_key_c0390e0f_like;
       public            health    false    302            �           1259    24101 (   encounters_clinic_Department_id_512b49f3    INDEX     s   CREATE INDEX "encounters_clinic_Department_id_512b49f3" ON public.encounters_clinic USING btree ("Department_id");
 >   DROP INDEX public."encounters_clinic_Department_id_512b49f3";
       public            health    false    259            �           1259    24100 $   encounters_clinic_name_8adb70d5_like    INDEX     v   CREATE INDEX encounters_clinic_name_8adb70d5_like ON public.encounters_clinic USING btree (name varchar_pattern_ops);
 8   DROP INDEX public.encounters_clinic_name_8adb70d5_like;
       public            health    false    259            �           1259    24109 /   encounters_encounter_encounter_id_acc9683d_like    INDEX     �   CREATE INDEX encounters_encounter_encounter_id_acc9683d_like ON public.encounters_encounter USING btree (encounter_id varchar_pattern_ops);
 C   DROP INDEX public.encounters_encounter_encounter_id_acc9683d_like;
       public            health    false    257            �           1259    24128 ,   encounters_encounter_type_name_6f6c7e2c_like    INDEX     �   CREATE INDEX encounters_encounter_type_name_6f6c7e2c_like ON public.encounters_encounter_type USING btree (name varchar_pattern_ops);
 @   DROP INDEX public.encounters_encounter_type_name_6f6c7e2c_like;
       public            health    false    261            �           1259    24088 &   encounters_status_status_2d14549d_like    INDEX     x   CREATE INDEX encounters_status_status_2d14549d_like ON public.encounters_status USING btree (name varchar_pattern_ops);
 :   DROP INDEX public.encounters_status_status_2d14549d_like;
       public            health    false    255            �           1259    24060 &   facilities_facility_name_3a317fbd_like    INDEX     z   CREATE INDEX facilities_facility_name_3a317fbd_like ON public.facilities_facility USING btree (name varchar_pattern_ops);
 :   DROP INDEX public.facilities_facility_name_3a317fbd_like;
       public            health    false    253            �           1259    24221 "   finance_bill_billed_to_id_32409d20    INDEX     c   CREATE INDEX finance_bill_billed_to_id_32409d20 ON public.finance_bill USING btree (billed_to_id);
 6   DROP INDEX public.finance_bill_billed_to_id_32409d20;
       public            health    false    273            �           1259    24187 ,   finance_billableitem_item_code_017a6bf0_like    INDEX     �   CREATE INDEX finance_billableitem_item_code_017a6bf0_like ON public.finance_billableitem USING btree (item_code varchar_pattern_ops);
 @   DROP INDEX public.finance_billableitem_item_code_017a6bf0_like;
       public            health    false    263            �           1259    24204 %   finance_payerscheme_payer_id_13747141    INDEX     i   CREATE INDEX finance_payerscheme_payer_id_13747141 ON public.finance_payerscheme USING btree (payer_id);
 9   DROP INDEX public.finance_payerscheme_payer_id_13747141;
       public            health    false    271            �           1259    24205 *   finance_payerscheme_price_list_id_3d41c464    INDEX     s   CREATE INDEX finance_payerscheme_price_list_id_3d41c464 ON public.finance_payerscheme USING btree (price_list_id);
 >   DROP INDEX public.finance_payerscheme_price_list_id_3d41c464;
       public            health    false    271                       1259    24542 *   finance_payment_payment_method_id_e7b7b54f    INDEX     s   CREATE INDEX finance_payment_payment_method_id_e7b7b54f ON public.finance_payment USING btree (payment_method_id);
 >   DROP INDEX public.finance_payment_payment_method_id_e7b7b54f;
       public            health    false    304            �           1259    24193 ,   finance_pricelistitem_price_list_id_89ae5a30    INDEX     w   CREATE INDEX finance_pricelistitem_price_list_id_89ae5a30 ON public.finance_pricelistitem USING btree (price_list_id);
 @   DROP INDEX public.finance_pricelistitem_price_list_id_89ae5a30;
       public            health    false    269            �           1259    24288 /   imaging_imagingobservation_lab_unit_id_d14d710c    INDEX     }   CREATE INDEX imaging_imagingobservation_lab_unit_id_d14d710c ON public.imaging_imagingobservation USING btree (img_unit_id);
 C   DROP INDEX public.imaging_imagingobservation_lab_unit_id_d14d710c;
       public            health    false    283            �           1259    24282 5   imaging_imagingobservationorder_img_order_id_d5f867dc    INDEX     �   CREATE INDEX imaging_imagingobservationorder_img_order_id_d5f867dc ON public.imaging_imagingobservationorder USING btree (img_order_id);
 I   DROP INDEX public.imaging_imagingobservationorder_img_order_id_d5f867dc;
       public            health    false    281            �           1259    24276 )   imaging_imagingorder_img_id_a9bfa6d8_like    INDEX     �   CREATE INDEX imaging_imagingorder_img_id_a9bfa6d8_like ON public.imaging_imagingorder USING btree (img_id varchar_pattern_ops);
 =   DROP INDEX public.imaging_imagingorder_img_id_a9bfa6d8_like;
       public            health    false    275                        1259    24357 %   laboratory_laborder_asn_af8e450f_like    INDEX     x   CREATE INDEX laboratory_laborder_asn_af8e450f_like ON public.laboratory_laborder USING btree (asn varchar_pattern_ops);
 9   DROP INDEX public.laboratory_laborder_asn_af8e450f_like;
       public            health    false    291                       1259    24363 .   laboratory_laborderpanel_lab_order_id_1c4b6f41    INDEX     {   CREATE INDEX laboratory_laborderpanel_lab_order_id_1c4b6f41 ON public.laboratory_labpanelorder USING btree (lab_order_id);
 B   DROP INDEX public.laboratory_laborderpanel_lab_order_id_1c4b6f41;
       public            health    false    293            �           1259    24399 $   laboratory_labpanel_type_id_9471a531    INDEX     p   CREATE INDEX laboratory_labpanel_type_id_9471a531 ON public.laboratory_labpanel USING btree (specimen_type_id);
 8   DROP INDEX public.laboratory_labpanel_type_id_9471a531;
       public            health    false    287            �           1259    24400 $   laboratory_labpanel_unit_id_090c53fe    INDEX     k   CREATE INDEX laboratory_labpanel_unit_id_090c53fe ON public.laboratory_labpanel USING btree (lab_unit_id);
 8   DROP INDEX public.laboratory_labpanel_unit_id_090c53fe;
       public            health    false    287                       1259    24449 "   patient_patient_uhid_8d67a08a_like    INDEX     r   CREATE INDEX patient_patient_uhid_8d67a08a_like ON public.patient_patient USING btree (uhid varchar_pattern_ops);
 6   DROP INDEX public.patient_patient_uhid_8d67a08a_like;
       public            health    false    301                       2606    23861 O   auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
       public          health    false    214    4472    218                       2606    23856 P   auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
       public          health    false    4477    216    218                       2606    23847 E   auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co;
       public          health    false    212    4467    214                       2606    23876 D   auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;
 n   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id;
       public          health    false    216    4477    222                        2606    23871 B   auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 l   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id;
       public          health    false    220    222    4485            !           2606    23890 S   auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm;
       public          health    false    214    4472    224            "           2606    23885 V   auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id;
       public          health    false    220    224    4485            %           2606    23934 @   authtoken_token authtoken_token_user_id_35299eff_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_35299eff_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 j   ALTER TABLE ONLY public.authtoken_token DROP CONSTRAINT authtoken_token_user_id_35299eff_fk_auth_user_id;
       public          health    false    220    4485    227            (           2606    24015 >   core_district core_district_state_id_ff1e236a_fk_core_state_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.core_district
    ADD CONSTRAINT core_district_state_id_ff1e236a_fk_core_state_id FOREIGN KEY (state_id) REFERENCES public.core_state(id) DEFERRABLE INITIALLY DEFERRED;
 h   ALTER TABLE ONLY public.core_district DROP CONSTRAINT core_district_state_id_ff1e236a_fk_core_state_id;
       public          health    false    241    4524    245            '           2606    24009 4   core_lga core_lga_state_id_9bdeff3f_fk_core_state_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.core_lga
    ADD CONSTRAINT core_lga_state_id_9bdeff3f_fk_core_state_id FOREIGN KEY (state_id) REFERENCES public.core_state(id) DEFERRABLE INITIALLY DEFERRED;
 ^   ALTER TABLE ONLY public.core_lga DROP CONSTRAINT core_lga_state_id_9bdeff3f_fk_core_state_id;
       public          health    false    241    4524    243            &           2606    24003 <   core_state core_state_country_id_5a16f697_fk_core_country_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.core_state
    ADD CONSTRAINT core_state_country_id_5a16f697_fk_core_country_id FOREIGN KEY (country_id) REFERENCES public.core_country(id) DEFERRABLE INITIALLY DEFERRED;
 f   ALTER TABLE ONLY public.core_state DROP CONSTRAINT core_state_country_id_5a16f697_fk_core_country_id;
       public          health    false    241    4511    229            #           2606    23907 G   django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co    FK CONSTRAINT     �   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 q   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co;
       public          health    false    226    4467    212            $           2606    23912 B   django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 l   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id;
       public          health    false    4485    220    226            )           2606    24095 G   encounters_clinic encounters_clinic_Department_id_512b49f3_fk_facilitie    FK CONSTRAINT     �   ALTER TABLE ONLY public.encounters_clinic
    ADD CONSTRAINT "encounters_clinic_Department_id_512b49f3_fk_facilitie" FOREIGN KEY ("Department_id") REFERENCES public.facilities_department(id) DEFERRABLE INITIALLY DEFERRED;
 s   ALTER TABLE ONLY public.encounters_clinic DROP CONSTRAINT "encounters_clinic_Department_id_512b49f3_fk_facilitie";
       public          health    false    259    251    4539            -           2606    24216 I   finance_bill finance_bill_billed_to_id_32409d20_fk_finance_payerscheme_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.finance_bill
    ADD CONSTRAINT finance_bill_billed_to_id_32409d20_fk_finance_payerscheme_id FOREIGN KEY (billed_to_id) REFERENCES public.finance_payerscheme(id) DEFERRABLE INITIALLY DEFERRED;
 s   ALTER TABLE ONLY public.finance_bill DROP CONSTRAINT finance_bill_billed_to_id_32409d20_fk_finance_payerscheme_id;
       public          health    false    4580    273    271            +           2606    24194 M   finance_payerscheme finance_payerscheme_payer_id_13747141_fk_finance_payer_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.finance_payerscheme
    ADD CONSTRAINT finance_payerscheme_payer_id_13747141_fk_finance_payer_id FOREIGN KEY (payer_id) REFERENCES public.finance_payer(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.finance_payerscheme DROP CONSTRAINT finance_payerscheme_payer_id_13747141_fk_finance_payer_id;
       public          health    false    4572    271    265            ,           2606    24199 K   finance_payerscheme finance_payerscheme_price_list_id_3d41c464_fk_finance_p    FK CONSTRAINT     �   ALTER TABLE ONLY public.finance_payerscheme
    ADD CONSTRAINT finance_payerscheme_price_list_id_3d41c464_fk_finance_p FOREIGN KEY (price_list_id) REFERENCES public.finance_pricelist(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.finance_payerscheme DROP CONSTRAINT finance_payerscheme_price_list_id_3d41c464_fk_finance_p;
       public          health    false    267    271    4574            3           2606    24537 G   finance_payment finance_payment_payment_method_id_e7b7b54f_fk_finance_p    FK CONSTRAINT     �   ALTER TABLE ONLY public.finance_payment
    ADD CONSTRAINT finance_payment_payment_method_id_e7b7b54f_fk_finance_p FOREIGN KEY (payment_method_id) REFERENCES public.finance_paymentmethod(id) DEFERRABLE INITIALLY DEFERRED;
 q   ALTER TABLE ONLY public.finance_payment DROP CONSTRAINT finance_payment_payment_method_id_e7b7b54f_fk_finance_p;
       public          health    false    4635    306    304            *           2606    24188 N   finance_pricelistitem finance_pricelistite_price_list_id_89ae5a30_fk_finance_p    FK CONSTRAINT     �   ALTER TABLE ONLY public.finance_pricelistitem
    ADD CONSTRAINT finance_pricelistite_price_list_id_89ae5a30_fk_finance_p FOREIGN KEY (price_list_id) REFERENCES public.finance_pricelist(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.finance_pricelistitem DROP CONSTRAINT finance_pricelistite_price_list_id_89ae5a30_fk_finance_p;
       public          health    false    269    4574    267            .           2606    24277 W   imaging_imagingobservationorder imaging_imagingobser_img_order_id_d5f867dc_fk_imaging_i    FK CONSTRAINT     �   ALTER TABLE ONLY public.imaging_imagingobservationorder
    ADD CONSTRAINT imaging_imagingobser_img_order_id_d5f867dc_fk_imaging_i FOREIGN KEY (img_order_id) REFERENCES public.imaging_imagingorder(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.imaging_imagingobservationorder DROP CONSTRAINT imaging_imagingobser_img_order_id_d5f867dc_fk_imaging_i;
       public          health    false    281    275    4589            /           2606    24294 Q   imaging_imagingobservation imaging_imagingobser_img_unit_id_07113642_fk_imaging_i    FK CONSTRAINT     �   ALTER TABLE ONLY public.imaging_imagingobservation
    ADD CONSTRAINT imaging_imagingobser_img_unit_id_07113642_fk_imaging_i FOREIGN KEY (img_unit_id) REFERENCES public.imaging_imagingunit(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.imaging_imagingobservation DROP CONSTRAINT imaging_imagingobser_img_unit_id_07113642_fk_imaging_i;
       public          health    false    277    283    4591            2           2606    24358 P   laboratory_labpanelorder laboratory_laborderp_lab_order_id_1c4b6f41_fk_laborator    FK CONSTRAINT     �   ALTER TABLE ONLY public.laboratory_labpanelorder
    ADD CONSTRAINT laboratory_laborderp_lab_order_id_1c4b6f41_fk_laborator FOREIGN KEY (lab_order_id) REFERENCES public.laboratory_laborder(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.laboratory_labpanelorder DROP CONSTRAINT laboratory_laborderp_lab_order_id_1c4b6f41_fk_laborator;
       public          health    false    293    291    4612            0           2606    24407 I   laboratory_labpanel laboratory_labpanel_lab_unit_id_d02636fe_fk_laborator    FK CONSTRAINT     �   ALTER TABLE ONLY public.laboratory_labpanel
    ADD CONSTRAINT laboratory_labpanel_lab_unit_id_d02636fe_fk_laborator FOREIGN KEY (lab_unit_id) REFERENCES public.laboratory_labunit(id) DEFERRABLE INITIALLY DEFERRED;
 s   ALTER TABLE ONLY public.laboratory_labpanel DROP CONSTRAINT laboratory_labpanel_lab_unit_id_d02636fe_fk_laborator;
       public          health    false    299    4621    287            1           2606    24412 N   laboratory_labpanel laboratory_labpanel_specimen_type_id_b1f8fcf5_fk_laborator    FK CONSTRAINT     �   ALTER TABLE ONLY public.laboratory_labpanel
    ADD CONSTRAINT laboratory_labpanel_specimen_type_id_b1f8fcf5_fk_laborator FOREIGN KEY (specimen_type_id) REFERENCES public.laboratory_labspecimentype(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.laboratory_labpanel DROP CONSTRAINT laboratory_labpanel_specimen_type_id_b1f8fcf5_fk_laborator;
       public          health    false    4619    297    287            �      x������ � �      �      x������ � �      �      x���I��6E��)t�8Kk_�KGT�$��aM!Qm��9}��މ���G23Re��p����|;m����*����p誀~��TR��q<�3�qH�&����_���Z{����c:�3�N/$D�
��ev��q����v-�0=p;{' �n���9K�4l�U{��,���q{݋&X�]	�����<#d�s�:݊��s|m0��teg�Og�����	��G`��������^�����f���E��2�m�ּP�����_A6Y�sJ�Z\?��X�`��\�X�ʐO�Z�Q1�'�It��+Az��<\c�� �cW�
��ct�DOP��' G�1��n���b���oWC��yrEd9#���tZ�<�B���q���0�v��!��v4�/��"�V�+�Ò�+��$��'G\����c#�](zf�h���|���Q�L��5��ps"
r\)�OD�W&�("4�/�c����g��zel�4]��+�d"���E�E���\���n���>�KA����k�(%����@�|[ڔ
���%�j�y:,.|�Z(��O%�n,I�4�c��O)���p~�4��|��~�lh�"��7����EҬ~h,JZ6���� ۋ�̰���傉h%��J:����˄��:(:����<����?ߛR��qW��Ӭ?N��1梌k �2�bdBI�vK�%M�[.SJ�|:�e~���*.|�z�r��;%!�-I�4Yn��N)��*�hQ������@��e2�p�e�䴡�֕���x�%Pq�����F����!Ñ�gkh�����kH���a:�@Ǖ�����b�SI�K�G!��&,�)UBg�kG�Hk�kƾJ{CDLsX�:��2�a�����Z�5l�z\Ŧ/n�  �2,T�dΰ�&�gvM��:��^�M�0�gb�L��1�e(���}ķ����}��r۬�PEi$Y׮�SuiTY׭�VUa֘�b���>��ۯ��U�v�f�+p�E���:\_r�5�ξj����jJ��}�����|±��t&���S�ªoft,${eN+q�>|����-�q��8�y��\"/�����U�>�*S���^OQ��Lz,����Z�]�o� ��!��2�Y�+�VI�0)�A\.���0�%��+6�C�mR�W�FѦ��BME��-��ݯ��%^��b�WY�f�|.$�j6�擊�z�>1��#V��:�E��ĖC�du˘΃Ȭj�T�D&5��$���
�Z݅��9�h�Fò~�ۨ,�9,ۭ4A�a�V�tN���|\ni�h�R�	x����LÛfԘj�q��|����k��i����Nڴ�u��M'm����_���k�L^W7������V��u�ǖ_j���.�<��R�{ʷ���_��.BE���~�E�6 ^_�&��m���6 ���Խ��f�T��Ӎ�
�ڤ8N����X�S"�.��vDk���ξ��]��R4q���˘+�N&�	$�4����hL��a	���>|�\m*zW�
�@cB^�#}D yK��i��+z�?`������=���,���� e_����f�J�oB�F��,W�R�����V4�w����E�N�d��DD��!I���y~���hZM�8��.K���E��Q�T�.I�k���X4��+wY�-�M�y$��1%摤�@*ʕ{���+|��z]��Sm�_Bi�L�|	��">}	��!�N�m.���v,��5=�}"A��J�@�B��	��)���9�?td��      �   �   x�]�M�0 @�ۯ��-��-��4�D[��_���'t�]���x�:��T*�r�Q<c�N��|H�A�6��S��d�#	C�ex~Ҥ�ju4'�yRJ��XɾX5�Ŕژ�/���'q�G,1���: ~�����۹��W�#A�����7!���2�      �      x������ � �      �      x������ � �      �   K   x���� �:�"}z�fI���?B�8}Y����5D%�s���]����,�&ǭ1�4�KD�K��"���      �   l  x�u�[o�0���a�W|8-�P.Z��LL0�=̍}�q�о��s��-F�u<2�0��%i ��}1����R ����p��P�;[��i��m\��`ց=#;6D�Kb��L�7��ϓ���sT�J��ɖ�q�E��n�u$v,��'閈	�F",����z#WX|���O� Oo����u�v�����O[��0��L�������pW��@�AjS\�U����'���=`������Z�g�kj�aG��;`ra�b����r�:]�m���j�"x\�w�U�"��m�yr&%�1�EAc����4@l��nk5uV����-+�zj��e/�?��嗈��?�A���]����(��_�2      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �   �  x�}�ے� ����t����Kg:+��<�w�/'�z��1�'�B̙&r��]
+f��I;��u�$�Kz��D1�w�*�_fh��D�n��+�u�xt�c�:>�٠����M�Z�%�+_��3�����Y6�RZ��y�!��eu'(i�˧%W�zc�Y���T��X@[A�vI{N���#�zv����(�@&��T@C�R>Rζ���\Av׆,e7�g�T���\B1teN�����_&��ȍ%GD�m�r7�gV�|�ɇ���|�utq=g�Ђ��N�$?�ۍHq�qFCyn���ҞT���(�l��kߩe4���\w޽������}����P�s�4�8��+Ӎln�"%�@�����+����Z}�U�|�G��	A��v��;����g4az�~� ��9IhX      �   �  x���ے�<���������:+ϲU�5j1x��y�mI�����&3c�?��܂S3����������o��N�2�������/�~QM,Pi�ߔ�`��>�� F� P�K�S}���;A���Vu����]�߮��>��i�AQ�`�媺�ۡ�>��R5_C۠�,I�J�Qk�U���S���H���ZH�қ�XUw�����4y��|u���:�_�Q�P��S�2�/�����k�v�)�!��b7�H)����p��a�c��C����fo�ov�
>g�H)�E�u�wo�ͼ��7Z"��J��tx��^T�]w����q
�w�8���MS})��i�5W28��3E�233DZ.��H�`��(����hPrE]P�q��� Di�LĨ���&r�m��N"�`Έ��2[8Ko�َt-N8ދ�̀���_��VpA��*�ؽ��QP(�*<@68��=�W��`���$ЌA�4��pJ�xO�6��f�p�	s�}���N��6����\]�h� ����)�o���%BR�ċ ������;J�Wy��?��1�5�������w#�V�SQ 0B��P|�>}�M��io���C�0sr}0��
b3��@�	�fb}�}m_���kEN�	8�p����om��	M�����!��D:4�D����=�/	�1�R�9ˎ����z�F����8�0�/�4Z�HMh�ο1������@�ɬ���
�қkn_�M��n"Xe`[��g{l������\�a�
�!�W(�(euвL�~��Db}��,=����4�E�+�)�� ���}bq�޺��!��O��QJ4�[P[d��ۗ�$�|��S8 ��'H8 K�	�=�G(��"U�_�,_@UM��	�U;�+��\�&#�rf��E�(pL�'�p�p���-Y��)��C�,�?�%��1��~	����gK� �/�i�}�7�����",�hR)V��oT��r��xx�����\��u8�;�̤ض5�<��y	���p��8o�x�4ŉ$���>J%�5	'H%e���Q�%ڦ��o���C������� vj�5��7���+e�����s�:w�������M��R�T�"%�1|�����>�g_���c����kb���)L�=�5�n��I=vu�R�|J-��GY\���P:E��u=A~LP�V�����S��j�0I{B���ؾ_Ň�[�I�F�f��
�Ö�ս+qp��+z�@�YSq���B�P�<G��5F��#<a���E��j���3h�����$�V���<;K&:'���J���I�����^��b�]�_%3��y�����T�����H�}Ě��Je瘤P<b`�H���dR\�SgL��C}?��#��}�q��j�N��a��bQ�Z��!8��t|u8��BG;g郳�SO}��3`à��D����@�/����s���,[;��R��q����#Q���d�] 2�ʕ'U�7���eNd�_��@i(�,:KPüW	� F%D��i���҇C����hO�Jm��'K?g~��F��u�����ot��@$���M����k�]�߯>xv*��M,d|D�6�����W�1��s#����6����ޙx%ܸ�(�����ލ���5C��[k`��a2<���u>�&�S�}a>[�2om3ߏ%��A�^�P�'ĕ�5���|�4���3?}��i�8��"���;��}����)S����0�<����BQ�EA�e2�4���Uơ'����k�������!_
p_s��_-�.���'���*a`�^���z�iQ��R�<S����B1�W�P۔��������l�Ҿ+���`�g6��ݨm�)��;R~�H����񡧠��6��\� �J�y������\��DXH�t��o���"�������Ǐ�V��           x��Ɏ�0  г|��'ZJ��q3�ںV������բ��)0�51婰��g��Fc6��K����l���wtp��\�~�\f��Uj2r�NK�-g� ���x���}G����Ɋ��Ľ�l^Õ��SO������w�$�߳.q"t�}�:�<rj�9aW���!�s�4��fD�<��板�.,����v7!K��h�������	k�vҮ�:T١N�<ݿ��7ABU#*@_��ȲbA��5M�+��X_�      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x��]��&��]�<E��UT1�dYr��8+�Ē�M��M�E5L�Օ��3�\��S8��/?����}��������_��W��?����~��߿���/������� ���f���X���
�����!���͓QȀ�B�f#�F�l�;���`n7�jr�Ѕ=:q���t*7]4t񢃸D��pL3��r�钡K{t�qNi�c64�Mǆ���л�	��t'Jj����=:p�S�8��h��7]6t��K��t����P@E��+����>rA�dzA�ჽ�38���|�j���Е6b�'����4�QPʲ2��8r�<櫨xP����--W&�\� ~B�Р'h���ʎ���m�?����R�>q(�*�S�m�#��O�
J9������/�ǫ��T` �.p�KZ㓘q�:O4�����.+�����ɏw���
h�ouY�+��1LԳ�Q�'q�[\xa���U�ơ�Du�d�i���xk���Z-h�ÖV�%F��Ά�^-FZp/o��KH����|FZ0mI%�8O~�R��� ����Wr�I*�ТՊϨ�.T˲�&���Y�q��K�K(��nhh��q!��*Q�,I�$u9Q���ڨ�ʈ���9���<QQۏ��Э.q�����[gr2CY��F^hO^:�N���D��3�Bak7�Kd k��&��ɨ�=>*�&���kh����P���4�_CE�>2�B��w�X$�0Y/�;y!��;ar�2ʓ/x�B�����M�% �q�r�z��L�f��]2���F-1�HL�]Fq�L2��f�s4"n������b�e�'�:Ff�-3a�3F�J:&lhWr#4��FpP��x�40{���4�/�����\2�?�f��Ԅ��1ʈi��OTT�Fj���4���I�҄>�y'.`I5'��AŦ`�&�)M,b��h��'�jOD�4��¼�L�d�6TԞ�Fh"lU.e��xMV�vI�2q�P��K90�H�hV�/������N�t6T��h&�
�p���$��o2�%��3�F��ʿ��%��B�^-F_⎾��D��k���n~F_"��\.��P�.T�h�%�aʈ5�,��d~M*@D#/1��c_��1_Cu�MF^�N��X����|^�.��Q�t����eȢ���R�Bu����$�(]ʈU }6b.���їt�|�L��:�2|����d�%��"�W�6bp�	�:5�;�ɨKZ������hw|d�%����Qʿ�L����$U'���6d*�+y�|���.a2꒔���	�!�)��!gM*=KF^�j� /��D��QQz�F_xY_ڈ�$`g�7�za�.���J|+����Q�]�V%�ʂ��D�	aAs-f�Q�M�R!�����P���p�&,��x���>`#1|K���9�3?Ө�P6êӛ� DWvNzfe�1�VI������U�D5���5態�Ar�b�G�W�z�ya-/�s;F��:Ҩ.��ȋ��B��BՐ!0M&x��b�Q���	��x���31
#���KB�2sml�+��1
#�¼�N�.	Υ��~b�E����mDp�2����P�0�/w��Q³5�����������/�Lfx��+�����")�y2�Qm��.";;�k�	>��cx1
#yg�s��ʐG)�����d����(J��l0)��a�Q�;;�RJ��#��P}����d���\�LF���\�n0e�0�v�<�,31�$Sh���ј���p�3#�:}Bx�	�'4��ޚ)�f(�lX^h�	��䴾�K��)�g��F���}��R>�8p�iT��l�%�
�=�?�̉"��D��"��*�������Pc��HEx����^��1KݜB��1cC�6�y0�Jb��gQ���[��:+!��k���%3�FI�&�E�dis��J��0*\.4F��߮�)�T�<���ڒ�a���+k5q�q�����1&Ø��XM�%}��5�y
=Fދ%���AWh�=�bes�X"P���P茚>��3�6dm汤�Xg�5z�|�K
��S~��5����`So0V�L��M��ެ{{ېU�&UŅ�c	0�^P��%�"a�yX7]h�h�F�{a%O,cf0I�������i�p5�r�ch�o'��F�1�,.�!s��H���D�O����w%� 睊��;�DS�3���f�DE���}e��`�E���
1��DK���������� {���06_P6߅\?W����
�{��|A�|ߗh��D%���*::�/���u2�k�6��|Fg��w�09,p��_�>1����}߄����31�aЭ#2��H'��ieV(i�������Rz݀�zR=�,���Kƈn�L�6�	BE�M���-y�#�j4@,�<`�Р��`�@�Lu�C)���ACחc���]$N���F���Q��}q>�!����Ѥ�1��2�.��]	�j�?�/(��"a�R�O	+�u,4�_�e�L2�T�T�Ņr�J��(��a*��˥P-�������%I�,҆js�/(��Ү|���K��mC�4��s��+iBx��K�����%��CX����1�_{B�q����r7C#4����� .�D�C�= B#4���D�eY�x0��M��Є��KmH�瞣���އ��a���g�\��(I�Pmyc���|���J)60�+0v�1�BX�w݆�%ڥ𼹫юϨL�SH���#�Ņ��~P�2����N�C��S&�ECQ�q�B�9�ncJd����*Qc���|��Y�Nb��7�}`��7Z4u��v�d��y`���d���D�F���B��gʐ9�Dv��O��#�/ĸ�/�F�ōJ����{B�%��F]��n|�/�͌��sY�㌦�I����A��
ap�'���g��Ch�F9����x�,�Ѯ�f<��<���:f�tc�	X�]-c\���rL.��8�:A����$��c����}��ؽL`�&��8��l7�w'0��+�m�� ��I����5J�6����ƺ�3���KǐT��j64t�8�!-��nC�,7ġ��F�γqCZ�gІDG��A�[�i��A��A�D4�e������g�qxVq�ة�q�r/�,7�8:���d�X�AY��k��`d��ѤW���a}��:�Ǆ�]�cޓ�W�$�6P�Oh4��oeC�{�xҝ9Ѯd����ײې��'��	v{�8��7��p|�t��L��W8�Q�/i��Ԍ!x�=So^�4��^hgWc���.����v��1��	MG%���O��G0ȞЄ�K)6:h��.y2�`���>Cfݠ�Ѳ��O0Ȟ�DX�Oi4�ho<� {J�Sm>��8���B�4��4k��#{�n����k�mH*'����U��"��R��8�h(���(��h�Q�/I��'mh�Z�1C�S�z�:-}O��%_0�=��ɕ��o�(���L�;o�7�C�=n�{����!��L��w�὘��ml�`l��|R�����P�t�؂!o�g����::��Q}�-�-���9+m��Л�X�AY�	3���
�~��Q��%Bp\��Oz����؃Aك��Cq8x�M�A/������"��C����h���wZ3P�Y}���/��q��i�C�7�]���1�ߑ�Ǻ1�<,+N��~��/��i׆��d�(P�d�!�i�@=׍�ǅ��~�$C�Ӟ�z�K%���r_(kB�/?��/�q1�\^?��_��_�����(��K�j�>Q�� �a��eW�x֚fQ�������.�Ǹ������.�~y��׉��fw���h�����p�V�x�������� ���K	�L�4v;�İ=��9[v�%k����
�l؞)���VAu���u�R��a{��s6p	�w���q�$�g��b=8��'�;Pֹu�*l���Hr��8Q}Ԋ�����>g �  S�/a>@�u�&���ɢ++��XLN�;6#&ʔ��r�ߖx�ҭ�%���lE�b�Q|����`��O���i�Ðs��1RRRj�o8N�C;)	FJ`p�eB�B������VF4ly9���M(����[4J�ϧ`��U���_�x���`4B��Bk�/�h��>`�njFG��99I>L~��:�E##����
E&�̬��������|Ζ�"(�(l��)�hT�3�x<�8�dj��Rn��t�&�K���L�r4*��z|N�]�o�5�'*�Ԍ�(�����jD��8����vGИ������	��@�ޙ����]f���({�;Y=��G���L�Qz>c4g��+���4�nnFF��Bڜ�K�8L�>hw�����|�&.$�y�vyd2B2����r����hI^h�id2J2�O��?��xI�h��Q���|�&�+џ�$�P�K�d�D{�_�D�G5�t��'�݇3ZB��ޜ�ϧ���r��Z�9^\���hQ^h�؈IX��Tҽ�@�~�وIX�F���v>h�71	��6Q����D���Q���&rxDv�7(��3j��D�_�^?���N��ql�$,��|���l(w����5A<�I�	[C��FM���9�z�����@�w�=1�~�W5��	q�)_`ĈI<Q4g���C���z��O]�5����t�E���B��#FN�O|av\� �r���J�=Q.��T�Qp��Ֆ�'�vf���ȓ(w��ȳ�φ���ߧ��){�Q~�A�K�(FQ��Яt�J6�.�뛋���1	����}g4%>/���Е��a��NT���b4E��&G���E���ջ.M�;�B��HƓ(�P�]6���C����ګ&���\hף�FS���.�R�BH�M~�Y��g�������v      �      x������ � �      �      x������ � �            x������ � �             x������ � �      �      x������ � �      �      x������ � �      	   u  x���YO#9���_�h���4�4������<�IJTʨZ���E�V��
	|^�=����P�%9*�s�J��4�d�e�E߯ѿ�!���cv�q��W�P��t��GWg��0����m�7����<�S�3��y�c��U(�@�I^��`)�N+�ZAa���u�<��q�)fE
��Z�e�%��i���ꨓ\��&֫������tQ3ʔ�V���U�Q����z�:lW�7Mں�lbrj��K��*�+�aJn�8	ӮPA�5:yrΰG�h��n*��T��q�����q�MHES^�N��<��BnC�R4�ؚ
��)��������H�(�3�]*�?h�������A��V9��i���b���(�c����v�mߒ���`�A6�"/��a=��I����ܠ�Xƚ|���e����fҕyM����YG��Q	�)��s�NcY8�U��6�E5#;7/�o�X����m1���|���`9N��L��r��D�QPΙa)�`��F�v���lR�ʻ/)�P�T�Co�O�¤���V��&�� 0){������y
e��Ch�Jax�-�n&ˎޕ�Fy�S:
�<�}>+�͗g�vֲTs	��B�s���!���סƁq�dz��\��P�Z��rca�0�[<D�G�|R�E=���y; �,�e갰(kC]u�u�א)c|��=�m__��
���ҩ�I����-e�V�^��T%ǒ������1��}r]} ��%w����.�����¬���|�·*������Ku��X�%�2̶�z�J��Dr�\b��2l�������H��Z�Ocl��w���i��4Xjt�
��k���U�8�s|d�<;[�W�� !!]�ۥ�Ҡ���&4 �#�NQ/�N���Ң�<�l��ۯ�ϟ7�>0!1p����X:tꗷ��'��E��S�5>U(Ű�({���8�,5F�c+�[:������Qed:p)�ջ��y�Jx	m#W�{��L�m%�z��I��?cQm׭��U��V�
�qP/�Cs�^�����]a�E����%��2X�%�<���W���M^����O�
�2�i��:�,:��[�� ��B�|������\��KNh�r���G�H�A�l*�k��'�Ta�p,UV��h�5[=� �Q�7��P-���v<>ۿ�}q �S%s�6�k�.*��/��]C���b^܏�)��K�
k�N��!Enm� ��H��5�����a_��כa�
�|\i��F'C7%�\i�J-�bm���JN&�8� ���6���k�NN���`�q˒��X;t�Ϫ /	��M��j�Ţ��3ruw���8(��O��aX{t<�Ծ���L��p��b���s�            x������ � �            x������ � �         7   x�3��M��S��,�4�4202�50�50T04�20"=SSCCm�=... �
	            x������ � �         r   x�3�tO�K-J���M���ጮV�K�MU�RP��57P��Q@��)X)��r"D<�JR�S��t��sJS���HF �r���(�Y�Y�YZ�jp��qqq ��"�            x������ � �            x���n#Gr���~����l�U���� ��YZ1-rw8̒�Ҝ�b8��|8 �ȳ�Q�$����q�������b$~P]����* ߷eq>×����$}W��}��{wh��ջ���v���.�e|㺬˶���^w��򽛺+��6~�bs(����|�����7��*��r�Ǣ�oJ!噰gJ,�~��B� �������\�e�*���s����?9���fA�C:���ܷ�ǕR��o� ����#����d���"���$��rյ��+��#��¤�h�Ȣ���:l3�8�A�x���eӴ�:�x��hH�Ԑ���~.�lVlV������8j���D� G7�^7�:rW<�e�~DJ��Y��@=�V������KfDq�P���Y�o�KmMH�U 
�Y�b�U����B�R�$ �[�4��K��$�Uc��F�$EA��i��سI]l^�U��UZ�o�u!EFSPDj6o�WR]�E�teUg��q#����6��&W���Qx������j��`�C�(W"hR(K$�7\2�f��)�uUl���Τ�x
��_/�ٳ�8��a(x2�NnV�� �
JE��0����lQ��S��l��_;�d�xu"bD)��s��n�����U��CsL����JyL��� C(!h�RYV��Td��t�f����\*&�z���YS���U6�6U{��=!�-0��OZ*��.2G�P�+�J,JG�%��%{�x}���́x.�:�$�toD�	H�e�ғ��u�}�ix��L*����\_g.F��քa�	#$�*An�]�v��k�D0	�$Ui�$k�|�6�C�\����E՛^��4�rߕm�yFD+.���%�h�Y����uU��P�4��$C�&�[v֛K�H4�JI�H,U�\|����m]u��wo_e�Ǡ~n8��(G�%�����?U�Q�mS�3n�r�A�TrMy��Ϟ��CQw��jUtUS���dHb
T�ބ�c6��e��q���4cdYiAU�M�D�xT�N8�bT2�=������:��R��9�5�ul�kI5����dO��;t����\[�SpՒ�o'(k����~Μ	pt���#���T� ��w�<$���Tx��@�5�}�6r7͞G���v$�֖j��Q�k�f7�Q�9��r����~!�y�h��!�S���k�i�?�0�+�!R@՞L6�O��~)��x`��%�Au ���j���㺁̡8.���U�F�
��
>X���Hj�\pvQm�6s�`&U�b5���e�"p�o����F���9��l�S�*��R>c��d�d߰�� W���I �C&��k��Ā�&�Qc�tS�k�r�]i�T%�p�1R�i<5��6Mם��U	����	�xrq��~��`&�db����@n��>���I|��J<�����V���CY���_n�����E�iW|0�7>��2��Z��瞝�	0��,�ܑǧF�b�e��RRԢtm��M�-�]��4-�:��|�f ����x�x��V����-��Z�����q�; å�*$ו�Vc��Ug�Y�e�˅V�xXj��c�A�lb�S����xe���䨵d�w�����_|�d��q"�T��zj����Qx��Vɼ��z�x��������x �1^�T��	j�lv/��*�拾�\e��zB �Vʔwq@��	i2�\�v:ECR=s�2�!9h�e��N�8�Y�GP��l
��N��儽��Y~`������o��rw%�;2��P��4����4u������2�c-�K����3�9�����w�:q�1#rơ"���%����Α��+��K��=+�8��&)I�u�����L2{�u�\5��ۑ4��KE��mjvΖ7�>����KT�T�m[u��W�ޛUly����^R�K�<�B���/^Q/��ɜpg�IU�xM=j۲��Z��Ŏ=n�"�c����[-lb{��zM��~(ٴjv���ɡ���W���4��ޓ0)��i�q�8Y��)�:7���޻)�q�ۓQu.�
I#d2�=��DT�돁P�ꤎ	��Pu�?lV�$w� ����^�R�v �I����7��T�$p"��ţ!�&���A���s�h�:^&��iP�,�\<2��-�04nٱ�%竖��Á`i@��V�lm��_�b���U欫\<+��BH./G�%�����_>�e�AqJk�G��O�#��զ��ܡX֕HEs�4�Tn*<Y���T�Þ]}g�͜K<4z�<�u. �\T��_r�2�)��3#q� �fU�<k����O6K���Ȭ���S��Hi>�<$�1D�:QW�.�H2��^�>͐��x\���L����;�EΓ�(�{+|�N2��
m�s������J�\�p,�!UW�%�1$j��j�����
2��ᐊEo�~*��ϻ��H��C���P������B<�V�M�z�t��~��vM�Mjn ��DƐ�@$������)G�� ���ͪɹ�@�ri��CP��6����jSu�l޴۾~��]�)ϯ�-�������$mJ��ib ����zė��m�PP��U"�q�(�L���|o��� Ȩ��ȯ7t�8>4Y��.�6=����:�vPւ!ӳ�U�6���C��Yb`���r�������cߕGk�x�����%7i��Ȥ^��I�b��HI��N��8We��O�M�5�k�]�K���*��␱8e�A��[��@н�J- �*��e[Uͺ�^^ۘ�.?�eַ�Bl*�,nЩ��D�+�,����Z�x)C*�$�\9P��f�|�����X��P&%p%
\�H�ћ��q���� Q�J}���q<#���m�56[�V<w^���(u���m�ܽ��2����W�%�zV:��XulQ�E�%W�7D��b9�9�">X%m�~P�ʡ�m��� q|���ȠP��@m�\��Ŭ{?L�?���n6�[�{tJ�)��qRY���XZk�<WU(n��S��7���W6A��U�\e�b��w%�pI�@���}��)�Xx�^�v�
Vir�sE$�ͭ�7>�^�W���.�%�3.ȔJS(^�Qc����(��s_��

�r�����2'�R��A�*S����>�y�Ax?l)#D4J�~�X�m��X!�HL��Tr7�܍p�*,�X��Y�2�!ё�ck�1(A�DO��Pq ��)�Q�jE��ۅ�����1(A�&�x�xSvl��.{,�8�N���ڐ��|�N,�V��1(G�%��]��1�a�n��v����$K,G�Z&��$՞<V�7�ԉ>58_�f}e����N�S��TǊ�f�������-W�ۍ���چjU#~��^��[
���z5@.�}U7��jS�N��H����'Ѡ���.�I.\*%W*Z��dz�0gá��]��0�I=�����h2���t��V�R95���rm9�]�0��$wg��ƒ���AAǮ6�s� s.�Ka �bQ��Abm�߳mѭ^P؝K�v�
A8gR�P�O&�PWk>�G�m����9 Ý�&�z-*_��OE��yQ�@��"�X��T'p��~� �r�ؼ��E&����$����3)�]�B�jv�{c��k)F�������c�HW���E~} (XԼV����͚���N��*��/����j��5͆MN�� �k�$Ծ��ܝ�r_I
�u��!	U��d^=����}�;{�s��$I����5����`Q[G��c��tnFѠ��\��f��]�d��6�Nr��m����^�S�cxl"3ܯ��*�	rY����+5���bA!�|,��d0�[����v�*a'�͡^���{���A=��|-O��V�Yy�v�rA)�4��^����O��-�ad�dP;C���çC�yz\���qB�I\9��Β�bS�U�9��±���Α>�:(A��S��e��o��g?��iƶ����8~���I����;t�-;	g�AE��XP�z   �er5e���އ<�+�4��H��췻���4�.4j�dBƣ���L��j8�<T�SXG�=7
un�P�xuH�[�:.m/(q�F{�U}Sߓ #�^�=F�����\��Hw�u�u���Eq�}�0lJ�qA��-y�����݂}nZvϟ�ϟ�?�>w�Q<g�xP�zT�E�5������3��)�M�
J^��c���îtgK�o���˼c�&�����9Og6h�>��~�1��Ipr\8�M��� �j��eW���[/��(;��̧�I�����EtH�T�A�4>eN#pm�������7���2oۀ�`��N�T���m�y��nE"��J�@}b��	Ј��"��r6��{��Q��b�^M&�Re��l�oTn���o��r碸�l�6�(cCl���J�<4�p�L3�(2!�'��X�9۞H0V$΃���"��^[89�A%.GK��$��M�}]W��@U�I,�ނL�%��Ga���l9�^6{�5���Ăʕ���i�>0���Ik/!I���sJ� (�            x������ � �            x������ � �           x����n1���SX�Turm_�eRB�(
�q�AXLg������,<����q��f"�;>��c��[>��#�����-�0 `��@8p~�J ejb&Ye�� N��[�����7��q�W��Ul`Y6ݾ�5}��5.�%V��X�����C����5tѵ!ڪ��"&�%y}�~^Z���L��Q��b��qz(��&��&�[��z��{���H�m��j�]��p!*�r����~K�hnE���I�?��цMMd���q�Gsf?D���� '�u�7�w-}�n���?�}׾,iX��S�� ��a�O>��b��0$w.����aLj����M�v�C���Fs�7U�d��y+�5y|�x|ˮtM��ˊ�6Ő�#�̑1��C������cꞞ�q,V�rF8;2{��߯���Ji�6o�I�
�@�y0�����<U�4#�,�d�խ�*���& �I9���YY��t޺�uV��Bi�g��E�u��}�*�0�shb@��%D��8#���-��>��GTV�18��}5�L~֤p         c   x�u̱�0�:������A�4T�/҆�t���z&IL
��&�]���n��ڝ&��.�A��~�5Z�����Ҡw��ы��<K��()            x������ � �            x������ � �     
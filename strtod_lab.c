#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <float.h>
#include <math.h>
#include <locale.h>
#include <stdint.h>
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L
#include <fenv.h>
#endif

typedef struct { int success; int hundredths; } r2d_res;
r2d_res parse_two_decimal(const char *s) {
    r2d_res r = {0,0};
    if(!s) return r;
    size_t len = strlen(s);
    if(len < 4 || len > 5) return r;
    int sign = 1;
    size_t pos = 0;
    if(s[0] == '+' || s[0] == '-') { if(s[0]=='-') sign=-1; pos=1; }
    if(strlen(s+pos) != 4) return r;
    if(s[pos+1] != '.') return r;
    char d0 = s[pos], d1 = s[pos+2], d2 = s[pos+3];
    if(d0<'0'||d0>'9'||d1<'0'||d1>'9'||d2<'0'||d2>'9') return r;
    int v = (d0-'0')*100 + (d1-'0')*10 + (d2-'0');
    if(v>999) return r;
    r.success=1;
    r.hundredths=sign*v;
    return r;
}

static void jstr(const char *s){ putchar('"'); for(;*s;s++){ unsigned char c=*s; if(c=='"'||c=='\\'){putchar('\\');putchar(c);} else if(c=='\n')fputs("\\n",stdout); else if(c=='\r')fputs("\\r",stdout); else if(c=='\t')fputs("\\t",stdout); else if(c<32)printf("\\u%04x",(int)c); else putchar(c);} putchar('"');}
static void jnum(double v){ if(isfinite(v)) printf("%.17g",v); else if(isnan(v)) fputs("null",stdout); else if(v>0) fputs("null",stdout); else fputs("null",stdout); }

int main(void){
    int has_nextafter=1, has_isnan=1, has_isinf=1, has_isfinite=1, has_signbit=1, has_fegetround=0, has_fesetround=0;
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L
    has_fegetround=1; has_fesetround=1;
#endif
    const char *init_loc = setlocale(LC_NUMERIC, NULL); if(!init_loc) init_loc="C";
    struct lconv *lc0 = localeconv(); const char *dec_pt0 = lc0 ? lc0->decimal_point : ".";
    printf("{");
    printf("\"compiler_probe\":{\"FLT_RADIX\":%d,\"DBL_MANT_DIG\":%d,\"DBL_MAX_EXP\":%d,\"sizeof_double\":%zu", FLT_RADIX, DBL_MANT_DIG, DBL_MAX_EXP, sizeof(double));
#ifdef __STDC_VERSION__
    printf(",\"stdc_version\":%ld", (long)__STDC_VERSION__);
#else
    printf(",\"stdc_version\":null");
#endif
    printf("},");
    printf("\"math_probe\":{\"nextafter\":%d,\"isnan\":%d,\"isinf\":%d,\"isfinite\":%d,\"signbit\":%d,\"fegetround\":%d,\"fesetround\":%d},", has_nextafter,has_isnan,has_isinf,has_isfinite,has_signbit,has_fegetround,has_fesetround);
    printf("\"locale_init\":"); jstr(init_loc); printf(",");
    printf("\"decimal_point_init\":"); jstr(dec_pt0); printf(",");

#define DO_STRTOD(tag__, input_str__) do{ \
    errno=0; const char *inp__ = input_str__; char *ep__=NULL; \
    double v__ = strtod(inp__, &ep__); int err__ = errno; \
    size_t off__ = ep__ ? (size_t)(ep__ - inp__) : 0; \
    int full__ = ep__ && ep__ == inp__ + strlen(inp__); \
    int conv__ = ep__ && ep__ != inp__; \
    printf("\"%s\":{\"input\":", tag__); jstr(inp__); \
    printf(",\"value\":"); jnum(v__); \
    printf(",\"value_hex\":\"%a\"", v__); \
    unsigned char *bp__=(unsigned char*)&v__; printf(",\"bytes\":\""); for(size_t bi__=0;bi__<sizeof(double);bi__++) printf("%02x", bp__[bi__]); printf("\""); \
    printf(",\"endptr_offset\":%zu", off__); \
    printf(",\"full\":%d,\"conversion\":%d", full__, conv__); \
    printf(",\"finite\":%d", isfinite(v__)); \
    printf(",\"isnan\":%d", isnan(v__)); \
    printf(",\"isinf\":%d", isinf(v__)); \
    printf(",\"signbit\":%d", signbit(v__)?1:0); \
    printf(",\"errno\":%d", err__); \
    if(ep__ && *ep__){ printf(",\"suffix\":"); jstr(ep__); } else { printf(",\"suffix\":\"\""); } \
    printf("},"); \
}while(0)

    DO_STRTOD("decimal_full", "42.125");
    DO_STRTOD("leading_space", " \t-12.5");
    DO_STRTOD("trailing_junk", "3.25xyz");
    DO_STRTOD("no_conversion", "xyz");

    errno = EDOM; char *eptmp; double vs = strtod("1.25", &eptmp); int err_stale = errno; size_t off_stale = (size_t)(eptmp - "1.25");
    errno = 0; double vs2 = strtod("1.25", &eptmp); int err_clean = errno; size_t off_clean = (size_t)(eptmp - "1.25");
    printf("\"stale_errno\":{\"v1\":"); jnum(vs); printf(",\"off1\":%zu,\"errno_after_stale\":%d,", off_stale, err_stale);
    printf("\"v2\":"); jnum(vs2); printf(",\"off2\":%zu,\"errno_after_clean\":%d},", off_clean, err_clean);

    DO_STRTOD("overflow", "1e5000");
    DO_STRTOD("underflow", "1e-5000");
    DO_STRTOD("signed_zero", "-0");
    DO_STRTOD("nan_token", "nan");

    errno=0; char *epinf1; double vinf1 = strtod("inf",&epinf1); int err_inf1=errno;
    errno=0; char *epinf2; double vinf2 = strtod("-infinity",&epinf2); int err_inf2=errno;
    printf("\"infinity\":{\"inf_input\":\"inf\",\"inf_value\":"); jnum(vinf1); printf(",\"inf_isinf\":%d,\"inf_signbit\":%d,\"inf_off\":%zu,\"inf_errno\":%d,", isinf(vinf1), signbit(vinf1)?1:0, (size_t)(epinf1-"inf"), err_inf1);
    printf("\"neg_input\":\"-infinity\",\"neg_value\":"); jnum(vinf2); printf(",\"neg_isinf\":%d,\"neg_signbit\":%d,\"neg_off\":%zu,\"neg_errno\":%d},", isinf(vinf2), signbit(vinf2)?1:0, (size_t)(epinf2-"-infinity"), err_inf2);

    DO_STRTOD("hex_float", "0x1.8p+1");

    char oldlocbuf[128]; strncpy(oldlocbuf, init_loc, sizeof(oldlocbuf)-1); oldlocbuf[sizeof(oldlocbuf)-1]=0;
    setlocale(LC_NUMERIC,"C");
    struct lconv *lc_c = localeconv();
    errno=0; char *epc1; double vc1=strtod("1.5",&epc1); int err_c1=errno;
    errno=0; char *epc2; double vc2=strtod("1,5",&epc2); int err_c2=errno;
    printf("\"c_locale\":{\"decimal_point\":"); jstr(lc_c?lc_c->decimal_point:".");
    printf(",\"dot_input\":\"1.5\",\"dot_value\":"); jnum(vc1); printf(",\"dot_off\":%zu,\"dot_errno\":%d,", (size_t)(epc1-"1.5"), err_c1);
    printf("\"comma_input\":\"1,5\",\"comma_value\":"); jnum(vc2); printf(",\"comma_off\":%zu,\"comma_errno\":%d,\"comma_suffix\":", (size_t)(epc2-"1,5"), err_c2); jstr(epc2); printf("},");
    setlocale(LC_NUMERIC, oldlocbuf);

    const char *cands[] = {"de_DE.UTF-8","de_DE.utf8","fr_FR.UTF-8","fr_FR.utf8",NULL};
    const char *found_loc=NULL; char found_dp[8]="."; double co_v1=0, co_v2=0; size_t co_o1=0, co_o2=0; int co_e1=0, co_e2=0; char co_s1[32]="", co_s2[32]="";
    for(int i=0;cands[i];i++){
        const char *r=setlocale(LC_NUMERIC,cands[i]);
        if(r){ struct lconv *l = localeconv(); if(l && l->decimal_point && strcmp(l->decimal_point,".")!=0){ found_loc=cands[i]; strncpy(found_dp, l->decimal_point, sizeof(found_dp)-1);
            errno=0; char *e1; co_v1=strtod("1,5",&e1); co_o1=(size_t)(e1-"1,5"); co_e1=errno; strncpy(co_s1, e1, sizeof(co_s1)-1);
            errno=0; char *e2; co_v2=strtod("1.5",&e2); co_o2=(size_t)(e2-"1.5"); co_e2=errno; strncpy(co_s2, e2, sizeof(co_s2)-1);
            break; } }
    }
    setlocale(LC_NUMERIC,"C");
    printf("\"comma_locale\":{\"found\":%s", found_loc?"true":"false");
    if(found_loc){ printf(",\"name\":"); jstr(found_loc); printf(",\"decimal_point\":"); jstr(found_dp);
        printf(",\"comma_value\":"); jnum(co_v1); printf(",\"comma_off\":%zu,\"comma_errno\":%d,\"comma_suffix\":", co_o1, co_e1); jstr(co_s1);
        printf(",\"dot_value\":"); jnum(co_v2); printf(",\"dot_off\":%zu,\"dot_errno\":%d,\"dot_suffix\":", co_o2, co_e2); jstr(co_s2); }
    printf("},");

    int can_round=0; double r1=0,r2=0,r3=0,n1=0; int rm_orig=-1;
    long double r1_ld=0,r2_ld=0,r3_ld=0;
    size_t ro1=0,ro2=0,ro3=0; int re1=0,re2=0,re3=0;
    if(FLT_RADIX==2 && DBL_MANT_DIG==53 && sizeof(double)==8 && has_fegetround && has_fesetround){
        rm_orig = fegetround();
        if(fesetround(FE_TONEAREST)==0){
            char *epr;
            errno=0; r1=strtod("1.00000000000000011102230246251565404236316680908203124",&epr); ro1=(size_t)(epr-"1.00000000000000011102230246251565404236316680908203124"); re1=errno;
            errno=0; r2=strtod("1.00000000000000011102230246251565404236316680908203125",&epr); ro2=(size_t)(epr-"1.00000000000000011102230246251565404236316680908203125"); re2=errno;
            errno=0; r3=strtod("1.00000000000000011102230246251565404236316680908203126",&epr); ro3=(size_t)(epr-"1.00000000000000011102230246251565404236316680908203126"); re3=errno;
            n1 = nextafter(1.0, 2.0);
            can_round=1;
            fesetround(rm_orig);
        }
    }
    printf("\"halfway\":{\"can_round\":%d", can_round);
    if(can_round){
        printf(",\"r1\":"); jnum(r1); printf(",\"r1_hex\":\"%a\",\"r1_off\":%zu,\"r1_errno\":%d", r1, ro1, re1);
        printf(",\"r2\":"); jnum(r2); printf(",\"r2_hex\":\"%a\",\"r2_off\":%zu,\"r2_errno\":%d", r2, ro2, re2);
        printf(",\"r3\":"); jnum(r3); printf(",\"r3_hex\":\"%a\",\"r3_off\":%zu,\"r3_errno\":%d", r3, ro3, re3);
        printf(",\"n1\":"); jnum(n1); printf(",\"n1_hex\":\"%a\",\"rounding_mode\":\"FE_TONEAREST\",\"rounding_mode_restored\":1", n1);
    }
    printf("},");

    char longtok[300]; for(int i=0;i<256;i++) longtok[i]='0'; strcpy(longtok+256,"1.25");
    errno=0; char *eplz; double vlz=strtod(longtok,&eplz); int err_lz=errno;
    size_t lz_off = (size_t)(eplz-longtok);
    printf("\"long_zero\":{\"token_len\":%zu,\"leading_zeros\":256,\"value\":", strlen(longtok)); jnum(vlz);
    printf(",\"value_hex\":\"%a\",\"offset\":%zu,\"full\":%d,\"errno\":%d},", vlz, lz_off, lz_off==strlen(longtok), err_lz);

    setlocale(LC_NUMERIC,"C");
    int total=0, succ=0, strtod_ok=0, match=0, first_fail=0; int has_fail=0;
    double max_err=0.0;
    for(int h=-999; h<=999; h++){
        total++;
        char tok[16]; int a = h<0?-h:h; snprintf(tok,sizeof(tok),"%s%d.%02d", h<0?"-":"", a/100, a%100);
        r2d_res rr = parse_two_decimal(tok);
        if(rr.success && rr.hundredths==h) succ++;
        char *epb; errno=0; double vd=strtod(tok,&epb);
        int full = epb && *epb=='\0';
        if(full) strtod_ok++;
        double scaled = vd*100.0;
        long rec = lround(scaled);
        double err = fabs(scaled - (double)rec);
        if(err>max_err) max_err=err;
        if(full && rec==h) match++;
        else if(!has_fail){ first_fail=h; has_fail=1; }
    }
    const char *rej_tokens[] = {"","1","1.2","10.00","1e2","nan","inf","1.00x"," 1.00","+1.000",NULL};
    int rej_results[32]={0}, rej_n=0;
    for(; rej_tokens[rej_n]; rej_n++){ r2d_res rr = parse_two_decimal(rej_tokens[rej_n]); rej_results[rej_n]=rr.success; }
    printf("\"bounded_parser\":{\"total\":%d,\"success\":%d,\"strtod_ok\":%d,\"match\":%d,\"first_fail\":", total, succ, strtod_ok, match);
    if(has_fail) printf("%d", first_fail); else printf("null");
    printf(",\"max_err\":%.17g,\"reject_tokens\":[", max_err);
    for(int i=0;i<rej_n;i++){ if(i)printf(","); printf("\""); const char *s=rej_tokens[i]; for(;*s;s++){ if(*s=='"'||*s=='\\')printf("\\%c",*s); else if(*s=='\n')printf("\\n"); else putchar(*s);} printf("\""); }
    printf("],\"reject_results\":[");
    for(int i=0;i<rej_n;i++){ if(i) printf(","); printf("%d", rej_results[i]); }
    printf("]},");

    const char *th_tokens[] = {"0.49999999999999994","0.5","0.50000000000000006","0.5score","nan","1e5000",NULL};
    printf("\"threshold\":{\"threshold\":0.5,\"cases\":[");
    for(int ti=0; th_tokens[ti]; ti++){
        if(ti) printf(",");
        const char *tt = th_tokens[ti];
        char *epth; errno=0; double vth=strtod(tt,&epth);
        int conv = epth && epth != tt;
        int full = conv && *epth=='\0';
        int err = errno;
        int finite = isfinite(vth);
        int naive_label = vth >= 0.5;
        int strict_valid = conv && full && err==34 ? 0 : (conv && full && err==0 && finite);
        if (conv && full && finite && err==0) strict_valid=1; else if(!(conv && full && finite)) strict_valid=0; else if(err==34) strict_valid=0;
        strict_valid = conv && full && err==0 && finite;
        int strict_label = strict_valid ? (vth >= 0.5) : -1;
        printf("{\"token\":"); jstr(tt);
        printf(",\"value\":"); jnum(vth); printf(",\"value_hex\":\"%a\"", vth);
        printf(",\"offset\":%ld,\"suffix\":", (long)(epth?epth-tt:0)); jstr(epth?epth:"");
        printf(",\"errno\":%d,\"finite\":%d,\"naive_label\":%d,\"strict_valid\":%d,\"strict_label\":%d}", err, finite, naive_label, strict_valid, strict_label);
    }
    printf("]}");
    printf("}\n");
    return 0;
}

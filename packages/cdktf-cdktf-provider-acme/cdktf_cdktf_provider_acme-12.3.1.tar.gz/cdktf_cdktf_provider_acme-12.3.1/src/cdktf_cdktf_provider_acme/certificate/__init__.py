r'''
# `acme_certificate`

Refer to the Terraform Registry for docs: [`acme_certificate`](https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class Certificate(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.certificate.Certificate",
):
    '''Represents a {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate acme_certificate}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        account_key_pem: builtins.str,
        certificate_p12_password: typing.Optional[builtins.str] = None,
        certificate_request_pem: typing.Optional[builtins.str] = None,
        cert_timeout: typing.Optional[jsii.Number] = None,
        common_name: typing.Optional[builtins.str] = None,
        disable_complete_propagation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dns_challenge: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CertificateDnsChallenge", typing.Dict[builtins.str, typing.Any]]]]] = None,
        http_challenge: typing.Optional[typing.Union["CertificateHttpChallenge", typing.Dict[builtins.str, typing.Any]]] = None,
        http_memcached_challenge: typing.Optional[typing.Union["CertificateHttpMemcachedChallenge", typing.Dict[builtins.str, typing.Any]]] = None,
        http_s3_challenge: typing.Optional[typing.Union["CertificateHttpS3Challenge", typing.Dict[builtins.str, typing.Any]]] = None,
        http_webroot_challenge: typing.Optional[typing.Union["CertificateHttpWebrootChallenge", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        min_days_remaining: typing.Optional[jsii.Number] = None,
        must_staple: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pre_check_delay: typing.Optional[jsii.Number] = None,
        preferred_chain: typing.Optional[builtins.str] = None,
        profile: typing.Optional[builtins.str] = None,
        recursive_nameservers: typing.Optional[typing.Sequence[builtins.str]] = None,
        renewal_info_ignore_retry_after: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        renewal_info_max_sleep: typing.Optional[jsii.Number] = None,
        revoke_certificate_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        revoke_certificate_reason: typing.Optional[builtins.str] = None,
        subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        tls_challenge: typing.Optional[typing.Union["CertificateTlsChallenge", typing.Dict[builtins.str, typing.Any]]] = None,
        use_renewal_info: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate acme_certificate} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_key_pem: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#account_key_pem Certificate#account_key_pem}.
        :param certificate_p12_password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#certificate_p12_password Certificate#certificate_p12_password}.
        :param certificate_request_pem: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#certificate_request_pem Certificate#certificate_request_pem}.
        :param cert_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#cert_timeout Certificate#cert_timeout}.
        :param common_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#common_name Certificate#common_name}.
        :param disable_complete_propagation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#disable_complete_propagation Certificate#disable_complete_propagation}.
        :param dns_challenge: dns_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#dns_challenge Certificate#dns_challenge}
        :param http_challenge: http_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_challenge Certificate#http_challenge}
        :param http_memcached_challenge: http_memcached_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_memcached_challenge Certificate#http_memcached_challenge}
        :param http_s3_challenge: http_s3_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_s3_challenge Certificate#http_s3_challenge}
        :param http_webroot_challenge: http_webroot_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_webroot_challenge Certificate#http_webroot_challenge}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#id Certificate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#key_type Certificate#key_type}.
        :param min_days_remaining: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#min_days_remaining Certificate#min_days_remaining}.
        :param must_staple: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#must_staple Certificate#must_staple}.
        :param pre_check_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#pre_check_delay Certificate#pre_check_delay}.
        :param preferred_chain: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#preferred_chain Certificate#preferred_chain}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#profile Certificate#profile}.
        :param recursive_nameservers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#recursive_nameservers Certificate#recursive_nameservers}.
        :param renewal_info_ignore_retry_after: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#renewal_info_ignore_retry_after Certificate#renewal_info_ignore_retry_after}.
        :param renewal_info_max_sleep: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#renewal_info_max_sleep Certificate#renewal_info_max_sleep}.
        :param revoke_certificate_on_destroy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#revoke_certificate_on_destroy Certificate#revoke_certificate_on_destroy}.
        :param revoke_certificate_reason: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#revoke_certificate_reason Certificate#revoke_certificate_reason}.
        :param subject_alternative_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#subject_alternative_names Certificate#subject_alternative_names}.
        :param tls_challenge: tls_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#tls_challenge Certificate#tls_challenge}
        :param use_renewal_info: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#use_renewal_info Certificate#use_renewal_info}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b8cd44b56a07d150dfbd98d06145dd331c94b87b184e8fa4cd61b39c9227d2d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CertificateConfig(
            account_key_pem=account_key_pem,
            certificate_p12_password=certificate_p12_password,
            certificate_request_pem=certificate_request_pem,
            cert_timeout=cert_timeout,
            common_name=common_name,
            disable_complete_propagation=disable_complete_propagation,
            dns_challenge=dns_challenge,
            http_challenge=http_challenge,
            http_memcached_challenge=http_memcached_challenge,
            http_s3_challenge=http_s3_challenge,
            http_webroot_challenge=http_webroot_challenge,
            id=id,
            key_type=key_type,
            min_days_remaining=min_days_remaining,
            must_staple=must_staple,
            pre_check_delay=pre_check_delay,
            preferred_chain=preferred_chain,
            profile=profile,
            recursive_nameservers=recursive_nameservers,
            renewal_info_ignore_retry_after=renewal_info_ignore_retry_after,
            renewal_info_max_sleep=renewal_info_max_sleep,
            revoke_certificate_on_destroy=revoke_certificate_on_destroy,
            revoke_certificate_reason=revoke_certificate_reason,
            subject_alternative_names=subject_alternative_names,
            tls_challenge=tls_challenge,
            use_renewal_info=use_renewal_info,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a Certificate resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Certificate to import.
        :param import_from_id: The id of the existing Certificate that should be imported. Refer to the {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Certificate to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b6507898670316f82024367c7586ed63e215243f8b2e4109de46c749df1280)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDnsChallenge")
    def put_dns_challenge(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CertificateDnsChallenge", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__316f06dc3b09b72fcbcd12941cec59c9082a2a3c454b19650b9fcde2350c7928)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDnsChallenge", [value]))

    @jsii.member(jsii_name="putHttpChallenge")
    def put_http_challenge(
        self,
        *,
        port: typing.Optional[jsii.Number] = None,
        proxy_header: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#port Certificate#port}.
        :param proxy_header: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#proxy_header Certificate#proxy_header}.
        '''
        value = CertificateHttpChallenge(port=port, proxy_header=proxy_header)

        return typing.cast(None, jsii.invoke(self, "putHttpChallenge", [value]))

    @jsii.member(jsii_name="putHttpMemcachedChallenge")
    def put_http_memcached_challenge(
        self,
        *,
        hosts: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param hosts: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#hosts Certificate#hosts}.
        '''
        value = CertificateHttpMemcachedChallenge(hosts=hosts)

        return typing.cast(None, jsii.invoke(self, "putHttpMemcachedChallenge", [value]))

    @jsii.member(jsii_name="putHttpS3Challenge")
    def put_http_s3_challenge(self, *, s3_bucket: builtins.str) -> None:
        '''
        :param s3_bucket: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#s3_bucket Certificate#s3_bucket}.
        '''
        value = CertificateHttpS3Challenge(s3_bucket=s3_bucket)

        return typing.cast(None, jsii.invoke(self, "putHttpS3Challenge", [value]))

    @jsii.member(jsii_name="putHttpWebrootChallenge")
    def put_http_webroot_challenge(self, *, directory: builtins.str) -> None:
        '''
        :param directory: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#directory Certificate#directory}.
        '''
        value = CertificateHttpWebrootChallenge(directory=directory)

        return typing.cast(None, jsii.invoke(self, "putHttpWebrootChallenge", [value]))

    @jsii.member(jsii_name="putTlsChallenge")
    def put_tls_challenge(self, *, port: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#port Certificate#port}.
        '''
        value = CertificateTlsChallenge(port=port)

        return typing.cast(None, jsii.invoke(self, "putTlsChallenge", [value]))

    @jsii.member(jsii_name="resetCertificateP12Password")
    def reset_certificate_p12_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateP12Password", []))

    @jsii.member(jsii_name="resetCertificateRequestPem")
    def reset_certificate_request_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateRequestPem", []))

    @jsii.member(jsii_name="resetCertTimeout")
    def reset_cert_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertTimeout", []))

    @jsii.member(jsii_name="resetCommonName")
    def reset_common_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommonName", []))

    @jsii.member(jsii_name="resetDisableCompletePropagation")
    def reset_disable_complete_propagation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableCompletePropagation", []))

    @jsii.member(jsii_name="resetDnsChallenge")
    def reset_dns_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsChallenge", []))

    @jsii.member(jsii_name="resetHttpChallenge")
    def reset_http_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpChallenge", []))

    @jsii.member(jsii_name="resetHttpMemcachedChallenge")
    def reset_http_memcached_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMemcachedChallenge", []))

    @jsii.member(jsii_name="resetHttpS3Challenge")
    def reset_http_s3_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpS3Challenge", []))

    @jsii.member(jsii_name="resetHttpWebrootChallenge")
    def reset_http_webroot_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpWebrootChallenge", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeyType")
    def reset_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyType", []))

    @jsii.member(jsii_name="resetMinDaysRemaining")
    def reset_min_days_remaining(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinDaysRemaining", []))

    @jsii.member(jsii_name="resetMustStaple")
    def reset_must_staple(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMustStaple", []))

    @jsii.member(jsii_name="resetPreCheckDelay")
    def reset_pre_check_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreCheckDelay", []))

    @jsii.member(jsii_name="resetPreferredChain")
    def reset_preferred_chain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredChain", []))

    @jsii.member(jsii_name="resetProfile")
    def reset_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfile", []))

    @jsii.member(jsii_name="resetRecursiveNameservers")
    def reset_recursive_nameservers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecursiveNameservers", []))

    @jsii.member(jsii_name="resetRenewalInfoIgnoreRetryAfter")
    def reset_renewal_info_ignore_retry_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRenewalInfoIgnoreRetryAfter", []))

    @jsii.member(jsii_name="resetRenewalInfoMaxSleep")
    def reset_renewal_info_max_sleep(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRenewalInfoMaxSleep", []))

    @jsii.member(jsii_name="resetRevokeCertificateOnDestroy")
    def reset_revoke_certificate_on_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevokeCertificateOnDestroy", []))

    @jsii.member(jsii_name="resetRevokeCertificateReason")
    def reset_revoke_certificate_reason(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevokeCertificateReason", []))

    @jsii.member(jsii_name="resetSubjectAlternativeNames")
    def reset_subject_alternative_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubjectAlternativeNames", []))

    @jsii.member(jsii_name="resetTlsChallenge")
    def reset_tls_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsChallenge", []))

    @jsii.member(jsii_name="resetUseRenewalInfo")
    def reset_use_renewal_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseRenewalInfo", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="certificateDomain")
    def certificate_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateDomain"))

    @builtins.property
    @jsii.member(jsii_name="certificateNotAfter")
    def certificate_not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateNotAfter"))

    @builtins.property
    @jsii.member(jsii_name="certificateP12")
    def certificate_p12(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateP12"))

    @builtins.property
    @jsii.member(jsii_name="certificatePem")
    def certificate_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificatePem"))

    @builtins.property
    @jsii.member(jsii_name="certificateSerial")
    def certificate_serial(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateSerial"))

    @builtins.property
    @jsii.member(jsii_name="certificateUrl")
    def certificate_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateUrl"))

    @builtins.property
    @jsii.member(jsii_name="dnsChallenge")
    def dns_challenge(self) -> "CertificateDnsChallengeList":
        return typing.cast("CertificateDnsChallengeList", jsii.get(self, "dnsChallenge"))

    @builtins.property
    @jsii.member(jsii_name="httpChallenge")
    def http_challenge(self) -> "CertificateHttpChallengeOutputReference":
        return typing.cast("CertificateHttpChallengeOutputReference", jsii.get(self, "httpChallenge"))

    @builtins.property
    @jsii.member(jsii_name="httpMemcachedChallenge")
    def http_memcached_challenge(
        self,
    ) -> "CertificateHttpMemcachedChallengeOutputReference":
        return typing.cast("CertificateHttpMemcachedChallengeOutputReference", jsii.get(self, "httpMemcachedChallenge"))

    @builtins.property
    @jsii.member(jsii_name="httpS3Challenge")
    def http_s3_challenge(self) -> "CertificateHttpS3ChallengeOutputReference":
        return typing.cast("CertificateHttpS3ChallengeOutputReference", jsii.get(self, "httpS3Challenge"))

    @builtins.property
    @jsii.member(jsii_name="httpWebrootChallenge")
    def http_webroot_challenge(
        self,
    ) -> "CertificateHttpWebrootChallengeOutputReference":
        return typing.cast("CertificateHttpWebrootChallengeOutputReference", jsii.get(self, "httpWebrootChallenge"))

    @builtins.property
    @jsii.member(jsii_name="issuerPem")
    def issuer_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerPem"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyPem")
    def private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPem"))

    @builtins.property
    @jsii.member(jsii_name="renewalInfoExplanationUrl")
    def renewal_info_explanation_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "renewalInfoExplanationUrl"))

    @builtins.property
    @jsii.member(jsii_name="renewalInfoRetryAfter")
    def renewal_info_retry_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "renewalInfoRetryAfter"))

    @builtins.property
    @jsii.member(jsii_name="renewalInfoWindowEnd")
    def renewal_info_window_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "renewalInfoWindowEnd"))

    @builtins.property
    @jsii.member(jsii_name="renewalInfoWindowSelected")
    def renewal_info_window_selected(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "renewalInfoWindowSelected"))

    @builtins.property
    @jsii.member(jsii_name="renewalInfoWindowStart")
    def renewal_info_window_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "renewalInfoWindowStart"))

    @builtins.property
    @jsii.member(jsii_name="tlsChallenge")
    def tls_challenge(self) -> "CertificateTlsChallengeOutputReference":
        return typing.cast("CertificateTlsChallengeOutputReference", jsii.get(self, "tlsChallenge"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyPemInput")
    def account_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountKeyPemInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateP12PasswordInput")
    def certificate_p12_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateP12PasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateRequestPemInput")
    def certificate_request_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateRequestPemInput"))

    @builtins.property
    @jsii.member(jsii_name="certTimeoutInput")
    def cert_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "certTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="disableCompletePropagationInput")
    def disable_complete_propagation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableCompletePropagationInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsChallengeInput")
    def dns_challenge_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CertificateDnsChallenge"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CertificateDnsChallenge"]]], jsii.get(self, "dnsChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="httpChallengeInput")
    def http_challenge_input(self) -> typing.Optional["CertificateHttpChallenge"]:
        return typing.cast(typing.Optional["CertificateHttpChallenge"], jsii.get(self, "httpChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMemcachedChallengeInput")
    def http_memcached_challenge_input(
        self,
    ) -> typing.Optional["CertificateHttpMemcachedChallenge"]:
        return typing.cast(typing.Optional["CertificateHttpMemcachedChallenge"], jsii.get(self, "httpMemcachedChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="httpS3ChallengeInput")
    def http_s3_challenge_input(self) -> typing.Optional["CertificateHttpS3Challenge"]:
        return typing.cast(typing.Optional["CertificateHttpS3Challenge"], jsii.get(self, "httpS3ChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="httpWebrootChallengeInput")
    def http_webroot_challenge_input(
        self,
    ) -> typing.Optional["CertificateHttpWebrootChallenge"]:
        return typing.cast(typing.Optional["CertificateHttpWebrootChallenge"], jsii.get(self, "httpWebrootChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="minDaysRemainingInput")
    def min_days_remaining_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minDaysRemainingInput"))

    @builtins.property
    @jsii.member(jsii_name="mustStapleInput")
    def must_staple_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "mustStapleInput"))

    @builtins.property
    @jsii.member(jsii_name="preCheckDelayInput")
    def pre_check_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "preCheckDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="preferredChainInput")
    def preferred_chain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredChainInput"))

    @builtins.property
    @jsii.member(jsii_name="profileInput")
    def profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileInput"))

    @builtins.property
    @jsii.member(jsii_name="recursiveNameserversInput")
    def recursive_nameservers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "recursiveNameserversInput"))

    @builtins.property
    @jsii.member(jsii_name="renewalInfoIgnoreRetryAfterInput")
    def renewal_info_ignore_retry_after_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "renewalInfoIgnoreRetryAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="renewalInfoMaxSleepInput")
    def renewal_info_max_sleep_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "renewalInfoMaxSleepInput"))

    @builtins.property
    @jsii.member(jsii_name="revokeCertificateOnDestroyInput")
    def revoke_certificate_on_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "revokeCertificateOnDestroyInput"))

    @builtins.property
    @jsii.member(jsii_name="revokeCertificateReasonInput")
    def revoke_certificate_reason_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "revokeCertificateReasonInput"))

    @builtins.property
    @jsii.member(jsii_name="subjectAlternativeNamesInput")
    def subject_alternative_names_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subjectAlternativeNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsChallengeInput")
    def tls_challenge_input(self) -> typing.Optional["CertificateTlsChallenge"]:
        return typing.cast(typing.Optional["CertificateTlsChallenge"], jsii.get(self, "tlsChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="useRenewalInfoInput")
    def use_renewal_info_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useRenewalInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyPem")
    def account_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountKeyPem"))

    @account_key_pem.setter
    def account_key_pem(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afb05ce4fc5cbad8c2010c744048566f77fbaa0234d21894e4487164ac9907c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountKeyPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificateP12Password")
    def certificate_p12_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateP12Password"))

    @certificate_p12_password.setter
    def certificate_p12_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__249087f3c68a627ba5ee96d4ebb27958195955b835b2550d136456679560ceb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateP12Password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificateRequestPem")
    def certificate_request_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateRequestPem"))

    @certificate_request_pem.setter
    def certificate_request_pem(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ed5fe280a22b325002f792af3aad565c117ec76bf73f8449f781044cb605387)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateRequestPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certTimeout")
    def cert_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "certTimeout"))

    @cert_timeout.setter
    def cert_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f2e211436c267999a97eaacd8f0b78ceb9414504fc8c9fd7ccdd5e329b8a9f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__334f17c97aa1347985e348d79894e86a7ff4193888b77d3f70473971fdb766f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableCompletePropagation")
    def disable_complete_propagation(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableCompletePropagation"))

    @disable_complete_propagation.setter
    def disable_complete_propagation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d68896f5036bf45936d5e8442a766f91211e921f55ca0efbb23abb5367726fb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableCompletePropagation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a17e8488f701b5b0c640fb4f6e135c72618e94b5d2828a0873144b665147786f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eac59fa59e1acdb46b58291d5fa489ceb7d036417025b6e31b9d5edaa200b437)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minDaysRemaining")
    def min_days_remaining(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minDaysRemaining"))

    @min_days_remaining.setter
    def min_days_remaining(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9343537e2f5d7fff10775f59bb380f55a2de7e0c11b6fd04bef5f6f8b325036)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minDaysRemaining", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mustStaple")
    def must_staple(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "mustStaple"))

    @must_staple.setter
    def must_staple(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a68e36bc4347ff98d62dfcc3a2231f5f111380a76c5a730660648ac22fba310)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mustStaple", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preCheckDelay")
    def pre_check_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "preCheckDelay"))

    @pre_check_delay.setter
    def pre_check_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4ad7f8e123f6a575d77c63997bc6781cafb0c0baa1c8f5e2de4eff0fbbd998c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preCheckDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferredChain")
    def preferred_chain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredChain"))

    @preferred_chain.setter
    def preferred_chain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__692aa3b8b65dbea6c3535bfe4f7bc80a6d68cb09851f051ac20e933929f29ae9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredChain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profile"))

    @profile.setter
    def profile(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f730a745640b3c05606ae3d61fb120576a7ddc2ab09f37c0c7e4fe9f8d6be8d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "profile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="recursiveNameservers")
    def recursive_nameservers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "recursiveNameservers"))

    @recursive_nameservers.setter
    def recursive_nameservers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bad5c764e17df3fe8b97dc65903fe5c73f88c7a671121d0ab2de0cd17972498)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recursiveNameservers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="renewalInfoIgnoreRetryAfter")
    def renewal_info_ignore_retry_after(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "renewalInfoIgnoreRetryAfter"))

    @renewal_info_ignore_retry_after.setter
    def renewal_info_ignore_retry_after(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29d5c4e6d43fb13d8f813567c97b35e882215956db5da9befaf71f6233f19845)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewalInfoIgnoreRetryAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="renewalInfoMaxSleep")
    def renewal_info_max_sleep(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "renewalInfoMaxSleep"))

    @renewal_info_max_sleep.setter
    def renewal_info_max_sleep(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e450b04c47379fb8d380147cd85c54896d46cefbde9e920c3f0c3f2ab5b7f51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewalInfoMaxSleep", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="revokeCertificateOnDestroy")
    def revoke_certificate_on_destroy(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "revokeCertificateOnDestroy"))

    @revoke_certificate_on_destroy.setter
    def revoke_certificate_on_destroy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e5f63fbaf9204ed33d3b2936fd01313bcaba25b4e02c456ff57033402b1ac9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revokeCertificateOnDestroy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="revokeCertificateReason")
    def revoke_certificate_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokeCertificateReason"))

    @revoke_certificate_reason.setter
    def revoke_certificate_reason(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d6ac4eb892aff4ae11a92f8e835332f196c00d58766efc96b9224716ac19fb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revokeCertificateReason", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subjectAlternativeNames")
    def subject_alternative_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subjectAlternativeNames"))

    @subject_alternative_names.setter
    def subject_alternative_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__242865a97369228750ff857e507cb4f5e99901b042526ab85485cc786d666a13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subjectAlternativeNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useRenewalInfo")
    def use_renewal_info(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useRenewalInfo"))

    @use_renewal_info.setter
    def use_renewal_info(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad6cbe7a6099766558e5434c0792d525a7e15e43e6d1910efcb260bda5b30a29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useRenewalInfo", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.certificate.CertificateConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_key_pem": "accountKeyPem",
        "certificate_p12_password": "certificateP12Password",
        "certificate_request_pem": "certificateRequestPem",
        "cert_timeout": "certTimeout",
        "common_name": "commonName",
        "disable_complete_propagation": "disableCompletePropagation",
        "dns_challenge": "dnsChallenge",
        "http_challenge": "httpChallenge",
        "http_memcached_challenge": "httpMemcachedChallenge",
        "http_s3_challenge": "httpS3Challenge",
        "http_webroot_challenge": "httpWebrootChallenge",
        "id": "id",
        "key_type": "keyType",
        "min_days_remaining": "minDaysRemaining",
        "must_staple": "mustStaple",
        "pre_check_delay": "preCheckDelay",
        "preferred_chain": "preferredChain",
        "profile": "profile",
        "recursive_nameservers": "recursiveNameservers",
        "renewal_info_ignore_retry_after": "renewalInfoIgnoreRetryAfter",
        "renewal_info_max_sleep": "renewalInfoMaxSleep",
        "revoke_certificate_on_destroy": "revokeCertificateOnDestroy",
        "revoke_certificate_reason": "revokeCertificateReason",
        "subject_alternative_names": "subjectAlternativeNames",
        "tls_challenge": "tlsChallenge",
        "use_renewal_info": "useRenewalInfo",
    },
)
class CertificateConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        account_key_pem: builtins.str,
        certificate_p12_password: typing.Optional[builtins.str] = None,
        certificate_request_pem: typing.Optional[builtins.str] = None,
        cert_timeout: typing.Optional[jsii.Number] = None,
        common_name: typing.Optional[builtins.str] = None,
        disable_complete_propagation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dns_challenge: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CertificateDnsChallenge", typing.Dict[builtins.str, typing.Any]]]]] = None,
        http_challenge: typing.Optional[typing.Union["CertificateHttpChallenge", typing.Dict[builtins.str, typing.Any]]] = None,
        http_memcached_challenge: typing.Optional[typing.Union["CertificateHttpMemcachedChallenge", typing.Dict[builtins.str, typing.Any]]] = None,
        http_s3_challenge: typing.Optional[typing.Union["CertificateHttpS3Challenge", typing.Dict[builtins.str, typing.Any]]] = None,
        http_webroot_challenge: typing.Optional[typing.Union["CertificateHttpWebrootChallenge", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        min_days_remaining: typing.Optional[jsii.Number] = None,
        must_staple: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pre_check_delay: typing.Optional[jsii.Number] = None,
        preferred_chain: typing.Optional[builtins.str] = None,
        profile: typing.Optional[builtins.str] = None,
        recursive_nameservers: typing.Optional[typing.Sequence[builtins.str]] = None,
        renewal_info_ignore_retry_after: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        renewal_info_max_sleep: typing.Optional[jsii.Number] = None,
        revoke_certificate_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        revoke_certificate_reason: typing.Optional[builtins.str] = None,
        subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        tls_challenge: typing.Optional[typing.Union["CertificateTlsChallenge", typing.Dict[builtins.str, typing.Any]]] = None,
        use_renewal_info: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_key_pem: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#account_key_pem Certificate#account_key_pem}.
        :param certificate_p12_password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#certificate_p12_password Certificate#certificate_p12_password}.
        :param certificate_request_pem: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#certificate_request_pem Certificate#certificate_request_pem}.
        :param cert_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#cert_timeout Certificate#cert_timeout}.
        :param common_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#common_name Certificate#common_name}.
        :param disable_complete_propagation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#disable_complete_propagation Certificate#disable_complete_propagation}.
        :param dns_challenge: dns_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#dns_challenge Certificate#dns_challenge}
        :param http_challenge: http_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_challenge Certificate#http_challenge}
        :param http_memcached_challenge: http_memcached_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_memcached_challenge Certificate#http_memcached_challenge}
        :param http_s3_challenge: http_s3_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_s3_challenge Certificate#http_s3_challenge}
        :param http_webroot_challenge: http_webroot_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_webroot_challenge Certificate#http_webroot_challenge}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#id Certificate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#key_type Certificate#key_type}.
        :param min_days_remaining: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#min_days_remaining Certificate#min_days_remaining}.
        :param must_staple: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#must_staple Certificate#must_staple}.
        :param pre_check_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#pre_check_delay Certificate#pre_check_delay}.
        :param preferred_chain: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#preferred_chain Certificate#preferred_chain}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#profile Certificate#profile}.
        :param recursive_nameservers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#recursive_nameservers Certificate#recursive_nameservers}.
        :param renewal_info_ignore_retry_after: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#renewal_info_ignore_retry_after Certificate#renewal_info_ignore_retry_after}.
        :param renewal_info_max_sleep: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#renewal_info_max_sleep Certificate#renewal_info_max_sleep}.
        :param revoke_certificate_on_destroy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#revoke_certificate_on_destroy Certificate#revoke_certificate_on_destroy}.
        :param revoke_certificate_reason: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#revoke_certificate_reason Certificate#revoke_certificate_reason}.
        :param subject_alternative_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#subject_alternative_names Certificate#subject_alternative_names}.
        :param tls_challenge: tls_challenge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#tls_challenge Certificate#tls_challenge}
        :param use_renewal_info: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#use_renewal_info Certificate#use_renewal_info}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(http_challenge, dict):
            http_challenge = CertificateHttpChallenge(**http_challenge)
        if isinstance(http_memcached_challenge, dict):
            http_memcached_challenge = CertificateHttpMemcachedChallenge(**http_memcached_challenge)
        if isinstance(http_s3_challenge, dict):
            http_s3_challenge = CertificateHttpS3Challenge(**http_s3_challenge)
        if isinstance(http_webroot_challenge, dict):
            http_webroot_challenge = CertificateHttpWebrootChallenge(**http_webroot_challenge)
        if isinstance(tls_challenge, dict):
            tls_challenge = CertificateTlsChallenge(**tls_challenge)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e234975ea4defe42d174617a2220fcc6d1248bdb19a0ddf36b6b0ccb066369c3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_key_pem", value=account_key_pem, expected_type=type_hints["account_key_pem"])
            check_type(argname="argument certificate_p12_password", value=certificate_p12_password, expected_type=type_hints["certificate_p12_password"])
            check_type(argname="argument certificate_request_pem", value=certificate_request_pem, expected_type=type_hints["certificate_request_pem"])
            check_type(argname="argument cert_timeout", value=cert_timeout, expected_type=type_hints["cert_timeout"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument disable_complete_propagation", value=disable_complete_propagation, expected_type=type_hints["disable_complete_propagation"])
            check_type(argname="argument dns_challenge", value=dns_challenge, expected_type=type_hints["dns_challenge"])
            check_type(argname="argument http_challenge", value=http_challenge, expected_type=type_hints["http_challenge"])
            check_type(argname="argument http_memcached_challenge", value=http_memcached_challenge, expected_type=type_hints["http_memcached_challenge"])
            check_type(argname="argument http_s3_challenge", value=http_s3_challenge, expected_type=type_hints["http_s3_challenge"])
            check_type(argname="argument http_webroot_challenge", value=http_webroot_challenge, expected_type=type_hints["http_webroot_challenge"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key_type", value=key_type, expected_type=type_hints["key_type"])
            check_type(argname="argument min_days_remaining", value=min_days_remaining, expected_type=type_hints["min_days_remaining"])
            check_type(argname="argument must_staple", value=must_staple, expected_type=type_hints["must_staple"])
            check_type(argname="argument pre_check_delay", value=pre_check_delay, expected_type=type_hints["pre_check_delay"])
            check_type(argname="argument preferred_chain", value=preferred_chain, expected_type=type_hints["preferred_chain"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument recursive_nameservers", value=recursive_nameservers, expected_type=type_hints["recursive_nameservers"])
            check_type(argname="argument renewal_info_ignore_retry_after", value=renewal_info_ignore_retry_after, expected_type=type_hints["renewal_info_ignore_retry_after"])
            check_type(argname="argument renewal_info_max_sleep", value=renewal_info_max_sleep, expected_type=type_hints["renewal_info_max_sleep"])
            check_type(argname="argument revoke_certificate_on_destroy", value=revoke_certificate_on_destroy, expected_type=type_hints["revoke_certificate_on_destroy"])
            check_type(argname="argument revoke_certificate_reason", value=revoke_certificate_reason, expected_type=type_hints["revoke_certificate_reason"])
            check_type(argname="argument subject_alternative_names", value=subject_alternative_names, expected_type=type_hints["subject_alternative_names"])
            check_type(argname="argument tls_challenge", value=tls_challenge, expected_type=type_hints["tls_challenge"])
            check_type(argname="argument use_renewal_info", value=use_renewal_info, expected_type=type_hints["use_renewal_info"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_key_pem": account_key_pem,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if certificate_p12_password is not None:
            self._values["certificate_p12_password"] = certificate_p12_password
        if certificate_request_pem is not None:
            self._values["certificate_request_pem"] = certificate_request_pem
        if cert_timeout is not None:
            self._values["cert_timeout"] = cert_timeout
        if common_name is not None:
            self._values["common_name"] = common_name
        if disable_complete_propagation is not None:
            self._values["disable_complete_propagation"] = disable_complete_propagation
        if dns_challenge is not None:
            self._values["dns_challenge"] = dns_challenge
        if http_challenge is not None:
            self._values["http_challenge"] = http_challenge
        if http_memcached_challenge is not None:
            self._values["http_memcached_challenge"] = http_memcached_challenge
        if http_s3_challenge is not None:
            self._values["http_s3_challenge"] = http_s3_challenge
        if http_webroot_challenge is not None:
            self._values["http_webroot_challenge"] = http_webroot_challenge
        if id is not None:
            self._values["id"] = id
        if key_type is not None:
            self._values["key_type"] = key_type
        if min_days_remaining is not None:
            self._values["min_days_remaining"] = min_days_remaining
        if must_staple is not None:
            self._values["must_staple"] = must_staple
        if pre_check_delay is not None:
            self._values["pre_check_delay"] = pre_check_delay
        if preferred_chain is not None:
            self._values["preferred_chain"] = preferred_chain
        if profile is not None:
            self._values["profile"] = profile
        if recursive_nameservers is not None:
            self._values["recursive_nameservers"] = recursive_nameservers
        if renewal_info_ignore_retry_after is not None:
            self._values["renewal_info_ignore_retry_after"] = renewal_info_ignore_retry_after
        if renewal_info_max_sleep is not None:
            self._values["renewal_info_max_sleep"] = renewal_info_max_sleep
        if revoke_certificate_on_destroy is not None:
            self._values["revoke_certificate_on_destroy"] = revoke_certificate_on_destroy
        if revoke_certificate_reason is not None:
            self._values["revoke_certificate_reason"] = revoke_certificate_reason
        if subject_alternative_names is not None:
            self._values["subject_alternative_names"] = subject_alternative_names
        if tls_challenge is not None:
            self._values["tls_challenge"] = tls_challenge
        if use_renewal_info is not None:
            self._values["use_renewal_info"] = use_renewal_info

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def account_key_pem(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#account_key_pem Certificate#account_key_pem}.'''
        result = self._values.get("account_key_pem")
        assert result is not None, "Required property 'account_key_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_p12_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#certificate_p12_password Certificate#certificate_p12_password}.'''
        result = self._values.get("certificate_p12_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_request_pem(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#certificate_request_pem Certificate#certificate_request_pem}.'''
        result = self._values.get("certificate_request_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#cert_timeout Certificate#cert_timeout}.'''
        result = self._values.get("cert_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def common_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#common_name Certificate#common_name}.'''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_complete_propagation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#disable_complete_propagation Certificate#disable_complete_propagation}.'''
        result = self._values.get("disable_complete_propagation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def dns_challenge(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CertificateDnsChallenge"]]]:
        '''dns_challenge block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#dns_challenge Certificate#dns_challenge}
        '''
        result = self._values.get("dns_challenge")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CertificateDnsChallenge"]]], result)

    @builtins.property
    def http_challenge(self) -> typing.Optional["CertificateHttpChallenge"]:
        '''http_challenge block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_challenge Certificate#http_challenge}
        '''
        result = self._values.get("http_challenge")
        return typing.cast(typing.Optional["CertificateHttpChallenge"], result)

    @builtins.property
    def http_memcached_challenge(
        self,
    ) -> typing.Optional["CertificateHttpMemcachedChallenge"]:
        '''http_memcached_challenge block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_memcached_challenge Certificate#http_memcached_challenge}
        '''
        result = self._values.get("http_memcached_challenge")
        return typing.cast(typing.Optional["CertificateHttpMemcachedChallenge"], result)

    @builtins.property
    def http_s3_challenge(self) -> typing.Optional["CertificateHttpS3Challenge"]:
        '''http_s3_challenge block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_s3_challenge Certificate#http_s3_challenge}
        '''
        result = self._values.get("http_s3_challenge")
        return typing.cast(typing.Optional["CertificateHttpS3Challenge"], result)

    @builtins.property
    def http_webroot_challenge(
        self,
    ) -> typing.Optional["CertificateHttpWebrootChallenge"]:
        '''http_webroot_challenge block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#http_webroot_challenge Certificate#http_webroot_challenge}
        '''
        result = self._values.get("http_webroot_challenge")
        return typing.cast(typing.Optional["CertificateHttpWebrootChallenge"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#id Certificate#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#key_type Certificate#key_type}.'''
        result = self._values.get("key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_days_remaining(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#min_days_remaining Certificate#min_days_remaining}.'''
        result = self._values.get("min_days_remaining")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def must_staple(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#must_staple Certificate#must_staple}.'''
        result = self._values.get("must_staple")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def pre_check_delay(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#pre_check_delay Certificate#pre_check_delay}.'''
        result = self._values.get("pre_check_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_chain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#preferred_chain Certificate#preferred_chain}.'''
        result = self._values.get("preferred_chain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#profile Certificate#profile}.'''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recursive_nameservers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#recursive_nameservers Certificate#recursive_nameservers}.'''
        result = self._values.get("recursive_nameservers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def renewal_info_ignore_retry_after(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#renewal_info_ignore_retry_after Certificate#renewal_info_ignore_retry_after}.'''
        result = self._values.get("renewal_info_ignore_retry_after")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def renewal_info_max_sleep(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#renewal_info_max_sleep Certificate#renewal_info_max_sleep}.'''
        result = self._values.get("renewal_info_max_sleep")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def revoke_certificate_on_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#revoke_certificate_on_destroy Certificate#revoke_certificate_on_destroy}.'''
        result = self._values.get("revoke_certificate_on_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def revoke_certificate_reason(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#revoke_certificate_reason Certificate#revoke_certificate_reason}.'''
        result = self._values.get("revoke_certificate_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subject_alternative_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#subject_alternative_names Certificate#subject_alternative_names}.'''
        result = self._values.get("subject_alternative_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tls_challenge(self) -> typing.Optional["CertificateTlsChallenge"]:
        '''tls_challenge block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#tls_challenge Certificate#tls_challenge}
        '''
        result = self._values.get("tls_challenge")
        return typing.cast(typing.Optional["CertificateTlsChallenge"], result)

    @builtins.property
    def use_renewal_info(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#use_renewal_info Certificate#use_renewal_info}.'''
        result = self._values.get("use_renewal_info")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.certificate.CertificateDnsChallenge",
    jsii_struct_bases=[],
    name_mapping={"provider": "provider", "config": "config"},
)
class CertificateDnsChallenge:
    def __init__(
        self,
        *,
        provider: builtins.str,
        config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#provider Certificate#provider}.
        :param config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#config Certificate#config}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d399ca72323e9fa9b274c9d22ab719e96d6d55d7529aea96d489f1f64480951)
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "provider": provider,
        }
        if config is not None:
            self._values["config"] = config

    @builtins.property
    def provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#provider Certificate#provider}.'''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#config Certificate#config}.'''
        result = self._values.get("config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateDnsChallenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateDnsChallengeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.certificate.CertificateDnsChallengeList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49d08589b69f9e54ab30428552131d1767aa8338a3871f2ccdb87f252207536a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "CertificateDnsChallengeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0149b8ce155215de184c4727eee9d2146b58654a8e5c146b8fa2a429d016458c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CertificateDnsChallengeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b6a3421422289edfb3d9168508745f0593104722e9503024ab9b698faf7b1e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32ed7cb7a3e44be4af7df5c8c09b39970b2edbb701661a3524b59bd95565f067)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faea14b17d0928bc818d8e3d675d5e560cfb0a15e3e31f206aaf4d4f381c0c7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CertificateDnsChallenge]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CertificateDnsChallenge]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CertificateDnsChallenge]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5aa2c3c87ac1092441461dc9b99a000074c50503eddc576c78dce0aa574ab27e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CertificateDnsChallengeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.certificate.CertificateDnsChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d318ad317d96f0afe87080b05bde5035e18c36d66d13ae13f140080aa7a34e02)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="providerInput")
    def provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerInput"))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "config"))

    @config.setter
    def config(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbd21f97f9958aa1cd019c1ea6547dcc8bb813720d6fc3fac311708c19471bbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8314b032d22666b4a1f854ec488be33514b107e95b9887e1a4cd479a67f87a23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CertificateDnsChallenge]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CertificateDnsChallenge]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CertificateDnsChallenge]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c822b0ec1f2be2fe5ebef2d4dfe5506bf0baae5c62aaa96de2f62efbfd0d442c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.certificate.CertificateHttpChallenge",
    jsii_struct_bases=[],
    name_mapping={"port": "port", "proxy_header": "proxyHeader"},
)
class CertificateHttpChallenge:
    def __init__(
        self,
        *,
        port: typing.Optional[jsii.Number] = None,
        proxy_header: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#port Certificate#port}.
        :param proxy_header: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#proxy_header Certificate#proxy_header}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a06b9a0662826e4a3b1ddaeecfa356e5a3f90a259b92338057a40a281c4428e)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument proxy_header", value=proxy_header, expected_type=type_hints["proxy_header"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if port is not None:
            self._values["port"] = port
        if proxy_header is not None:
            self._values["proxy_header"] = proxy_header

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#port Certificate#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def proxy_header(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#proxy_header Certificate#proxy_header}.'''
        result = self._values.get("proxy_header")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateHttpChallenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateHttpChallengeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.certificate.CertificateHttpChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fff567a86d63262ae011ce813cecd8ef2da39df61ef62ee8e9655a5bfdda0b7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetProxyHeader")
    def reset_proxy_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProxyHeader", []))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="proxyHeaderInput")
    def proxy_header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "proxyHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d39d4b6719d8b176d3776096275f193b872281bbfaa2955b959c1b7fc6267d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="proxyHeader")
    def proxy_header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "proxyHeader"))

    @proxy_header.setter
    def proxy_header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8588888c7f3d743ff264ad594ec846b542ba18ab8c2476aafca0dcea41ac2a95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxyHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CertificateHttpChallenge]:
        return typing.cast(typing.Optional[CertificateHttpChallenge], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[CertificateHttpChallenge]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2103c4d5bd9ccbc5b41fdf27bb786ac6712fa875bbea700976dd2bdc766349ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.certificate.CertificateHttpMemcachedChallenge",
    jsii_struct_bases=[],
    name_mapping={"hosts": "hosts"},
)
class CertificateHttpMemcachedChallenge:
    def __init__(self, *, hosts: typing.Sequence[builtins.str]) -> None:
        '''
        :param hosts: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#hosts Certificate#hosts}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__605409a4bee15f8b6bcfaf45521120d45150c389f7588057d7b80c1f42e2d9ae)
            check_type(argname="argument hosts", value=hosts, expected_type=type_hints["hosts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hosts": hosts,
        }

    @builtins.property
    def hosts(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#hosts Certificate#hosts}.'''
        result = self._values.get("hosts")
        assert result is not None, "Required property 'hosts' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateHttpMemcachedChallenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateHttpMemcachedChallengeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.certificate.CertificateHttpMemcachedChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa59c1db9c06ff9e57cbe11bf896a4e29a4fdb1cd2420f69562316f8c7e0dad5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="hostsInput")
    def hosts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "hostsInput"))

    @builtins.property
    @jsii.member(jsii_name="hosts")
    def hosts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "hosts"))

    @hosts.setter
    def hosts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0ec37339e85235fb22702b24431cef78ae2af4e0e47fe72edfcd4fea1539201)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hosts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CertificateHttpMemcachedChallenge]:
        return typing.cast(typing.Optional[CertificateHttpMemcachedChallenge], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CertificateHttpMemcachedChallenge],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f992677746418c2fdc019ba79dfd620d731e02e4cc32b6f00a09fe2e276e61f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.certificate.CertificateHttpS3Challenge",
    jsii_struct_bases=[],
    name_mapping={"s3_bucket": "s3Bucket"},
)
class CertificateHttpS3Challenge:
    def __init__(self, *, s3_bucket: builtins.str) -> None:
        '''
        :param s3_bucket: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#s3_bucket Certificate#s3_bucket}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__340a44f2ee7e4ada999bb1cf87ccb90474c893a565d7bb31d7e8a45caf51acc0)
            check_type(argname="argument s3_bucket", value=s3_bucket, expected_type=type_hints["s3_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_bucket": s3_bucket,
        }

    @builtins.property
    def s3_bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#s3_bucket Certificate#s3_bucket}.'''
        result = self._values.get("s3_bucket")
        assert result is not None, "Required property 's3_bucket' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateHttpS3Challenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateHttpS3ChallengeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.certificate.CertificateHttpS3ChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddff2d15476435827bd344c64b14fddcf00c0fa634af4b25ee6d321da213a5a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="s3BucketInput")
    def s3_bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3BucketInput"))

    @builtins.property
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Bucket"))

    @s3_bucket.setter
    def s3_bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0f65c84a2fc4338b7ac779a44580bc667f91417d85a5128777ed7b1a7134103)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3Bucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CertificateHttpS3Challenge]:
        return typing.cast(typing.Optional[CertificateHttpS3Challenge], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CertificateHttpS3Challenge],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9dd58b743326e186118958a66a6658b78d6b33630dd18f504b1f5e685d6aa8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.certificate.CertificateHttpWebrootChallenge",
    jsii_struct_bases=[],
    name_mapping={"directory": "directory"},
)
class CertificateHttpWebrootChallenge:
    def __init__(self, *, directory: builtins.str) -> None:
        '''
        :param directory: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#directory Certificate#directory}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf8d6c9ec9e9ff59762c8dc206bc3e4982059675c841150c5ed60197eb5c1140)
            check_type(argname="argument directory", value=directory, expected_type=type_hints["directory"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "directory": directory,
        }

    @builtins.property
    def directory(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#directory Certificate#directory}.'''
        result = self._values.get("directory")
        assert result is not None, "Required property 'directory' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateHttpWebrootChallenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateHttpWebrootChallengeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.certificate.CertificateHttpWebrootChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db3e907af81f5d87a81d1f1176f20cc00b50ecec623460f63c56d9a4474dd73c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="directoryInput")
    def directory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryInput"))

    @builtins.property
    @jsii.member(jsii_name="directory")
    def directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directory"))

    @directory.setter
    def directory(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6f75163fa53c0a6000c3c0c77235b9fceee7154df1f2b7cc53de5dfe42a6e06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directory", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CertificateHttpWebrootChallenge]:
        return typing.cast(typing.Optional[CertificateHttpWebrootChallenge], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CertificateHttpWebrootChallenge],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__995b3fd1de1a09e12b5eef4fe62baf6b1eebb99a5ada9e3ac7e62ed00df2c59e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.certificate.CertificateTlsChallenge",
    jsii_struct_bases=[],
    name_mapping={"port": "port"},
)
class CertificateTlsChallenge:
    def __init__(self, *, port: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#port Certificate#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0a778adc41a2b38670f36d3b2542d792118b577dc80709ef033ca9ce3e12a19)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/certificate#port Certificate#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateTlsChallenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateTlsChallengeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.certificate.CertificateTlsChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dddd1443cf652107dd160bf36fc4761ac7902b1745536601a8d27d93f398417a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19c18efa7592ff166fcd8a7237e29cdfbf6e494dc5b4b7f64fad8441b83291cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CertificateTlsChallenge]:
        return typing.cast(typing.Optional[CertificateTlsChallenge], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[CertificateTlsChallenge]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__909933c29e9cbb8c06f132f102d101920ddd66b54c3a1dc16523ed12cd95acb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Certificate",
    "CertificateConfig",
    "CertificateDnsChallenge",
    "CertificateDnsChallengeList",
    "CertificateDnsChallengeOutputReference",
    "CertificateHttpChallenge",
    "CertificateHttpChallengeOutputReference",
    "CertificateHttpMemcachedChallenge",
    "CertificateHttpMemcachedChallengeOutputReference",
    "CertificateHttpS3Challenge",
    "CertificateHttpS3ChallengeOutputReference",
    "CertificateHttpWebrootChallenge",
    "CertificateHttpWebrootChallengeOutputReference",
    "CertificateTlsChallenge",
    "CertificateTlsChallengeOutputReference",
]

publication.publish()

def _typecheckingstub__4b8cd44b56a07d150dfbd98d06145dd331c94b87b184e8fa4cd61b39c9227d2d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    account_key_pem: builtins.str,
    certificate_p12_password: typing.Optional[builtins.str] = None,
    certificate_request_pem: typing.Optional[builtins.str] = None,
    cert_timeout: typing.Optional[jsii.Number] = None,
    common_name: typing.Optional[builtins.str] = None,
    disable_complete_propagation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dns_challenge: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CertificateDnsChallenge, typing.Dict[builtins.str, typing.Any]]]]] = None,
    http_challenge: typing.Optional[typing.Union[CertificateHttpChallenge, typing.Dict[builtins.str, typing.Any]]] = None,
    http_memcached_challenge: typing.Optional[typing.Union[CertificateHttpMemcachedChallenge, typing.Dict[builtins.str, typing.Any]]] = None,
    http_s3_challenge: typing.Optional[typing.Union[CertificateHttpS3Challenge, typing.Dict[builtins.str, typing.Any]]] = None,
    http_webroot_challenge: typing.Optional[typing.Union[CertificateHttpWebrootChallenge, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    key_type: typing.Optional[builtins.str] = None,
    min_days_remaining: typing.Optional[jsii.Number] = None,
    must_staple: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    pre_check_delay: typing.Optional[jsii.Number] = None,
    preferred_chain: typing.Optional[builtins.str] = None,
    profile: typing.Optional[builtins.str] = None,
    recursive_nameservers: typing.Optional[typing.Sequence[builtins.str]] = None,
    renewal_info_ignore_retry_after: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    renewal_info_max_sleep: typing.Optional[jsii.Number] = None,
    revoke_certificate_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    revoke_certificate_reason: typing.Optional[builtins.str] = None,
    subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    tls_challenge: typing.Optional[typing.Union[CertificateTlsChallenge, typing.Dict[builtins.str, typing.Any]]] = None,
    use_renewal_info: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b6507898670316f82024367c7586ed63e215243f8b2e4109de46c749df1280(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__316f06dc3b09b72fcbcd12941cec59c9082a2a3c454b19650b9fcde2350c7928(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CertificateDnsChallenge, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afb05ce4fc5cbad8c2010c744048566f77fbaa0234d21894e4487164ac9907c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__249087f3c68a627ba5ee96d4ebb27958195955b835b2550d136456679560ceb0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ed5fe280a22b325002f792af3aad565c117ec76bf73f8449f781044cb605387(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f2e211436c267999a97eaacd8f0b78ceb9414504fc8c9fd7ccdd5e329b8a9f4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__334f17c97aa1347985e348d79894e86a7ff4193888b77d3f70473971fdb766f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d68896f5036bf45936d5e8442a766f91211e921f55ca0efbb23abb5367726fb0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a17e8488f701b5b0c640fb4f6e135c72618e94b5d2828a0873144b665147786f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eac59fa59e1acdb46b58291d5fa489ceb7d036417025b6e31b9d5edaa200b437(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9343537e2f5d7fff10775f59bb380f55a2de7e0c11b6fd04bef5f6f8b325036(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a68e36bc4347ff98d62dfcc3a2231f5f111380a76c5a730660648ac22fba310(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4ad7f8e123f6a575d77c63997bc6781cafb0c0baa1c8f5e2de4eff0fbbd998c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__692aa3b8b65dbea6c3535bfe4f7bc80a6d68cb09851f051ac20e933929f29ae9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f730a745640b3c05606ae3d61fb120576a7ddc2ab09f37c0c7e4fe9f8d6be8d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bad5c764e17df3fe8b97dc65903fe5c73f88c7a671121d0ab2de0cd17972498(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29d5c4e6d43fb13d8f813567c97b35e882215956db5da9befaf71f6233f19845(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e450b04c47379fb8d380147cd85c54896d46cefbde9e920c3f0c3f2ab5b7f51(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e5f63fbaf9204ed33d3b2936fd01313bcaba25b4e02c456ff57033402b1ac9d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d6ac4eb892aff4ae11a92f8e835332f196c00d58766efc96b9224716ac19fb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__242865a97369228750ff857e507cb4f5e99901b042526ab85485cc786d666a13(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad6cbe7a6099766558e5434c0792d525a7e15e43e6d1910efcb260bda5b30a29(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e234975ea4defe42d174617a2220fcc6d1248bdb19a0ddf36b6b0ccb066369c3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_key_pem: builtins.str,
    certificate_p12_password: typing.Optional[builtins.str] = None,
    certificate_request_pem: typing.Optional[builtins.str] = None,
    cert_timeout: typing.Optional[jsii.Number] = None,
    common_name: typing.Optional[builtins.str] = None,
    disable_complete_propagation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dns_challenge: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CertificateDnsChallenge, typing.Dict[builtins.str, typing.Any]]]]] = None,
    http_challenge: typing.Optional[typing.Union[CertificateHttpChallenge, typing.Dict[builtins.str, typing.Any]]] = None,
    http_memcached_challenge: typing.Optional[typing.Union[CertificateHttpMemcachedChallenge, typing.Dict[builtins.str, typing.Any]]] = None,
    http_s3_challenge: typing.Optional[typing.Union[CertificateHttpS3Challenge, typing.Dict[builtins.str, typing.Any]]] = None,
    http_webroot_challenge: typing.Optional[typing.Union[CertificateHttpWebrootChallenge, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    key_type: typing.Optional[builtins.str] = None,
    min_days_remaining: typing.Optional[jsii.Number] = None,
    must_staple: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    pre_check_delay: typing.Optional[jsii.Number] = None,
    preferred_chain: typing.Optional[builtins.str] = None,
    profile: typing.Optional[builtins.str] = None,
    recursive_nameservers: typing.Optional[typing.Sequence[builtins.str]] = None,
    renewal_info_ignore_retry_after: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    renewal_info_max_sleep: typing.Optional[jsii.Number] = None,
    revoke_certificate_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    revoke_certificate_reason: typing.Optional[builtins.str] = None,
    subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    tls_challenge: typing.Optional[typing.Union[CertificateTlsChallenge, typing.Dict[builtins.str, typing.Any]]] = None,
    use_renewal_info: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d399ca72323e9fa9b274c9d22ab719e96d6d55d7529aea96d489f1f64480951(
    *,
    provider: builtins.str,
    config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49d08589b69f9e54ab30428552131d1767aa8338a3871f2ccdb87f252207536a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0149b8ce155215de184c4727eee9d2146b58654a8e5c146b8fa2a429d016458c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b6a3421422289edfb3d9168508745f0593104722e9503024ab9b698faf7b1e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32ed7cb7a3e44be4af7df5c8c09b39970b2edbb701661a3524b59bd95565f067(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faea14b17d0928bc818d8e3d675d5e560cfb0a15e3e31f206aaf4d4f381c0c7d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aa2c3c87ac1092441461dc9b99a000074c50503eddc576c78dce0aa574ab27e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CertificateDnsChallenge]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d318ad317d96f0afe87080b05bde5035e18c36d66d13ae13f140080aa7a34e02(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbd21f97f9958aa1cd019c1ea6547dcc8bb813720d6fc3fac311708c19471bbb(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8314b032d22666b4a1f854ec488be33514b107e95b9887e1a4cd479a67f87a23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c822b0ec1f2be2fe5ebef2d4dfe5506bf0baae5c62aaa96de2f62efbfd0d442c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CertificateDnsChallenge]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a06b9a0662826e4a3b1ddaeecfa356e5a3f90a259b92338057a40a281c4428e(
    *,
    port: typing.Optional[jsii.Number] = None,
    proxy_header: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fff567a86d63262ae011ce813cecd8ef2da39df61ef62ee8e9655a5bfdda0b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d39d4b6719d8b176d3776096275f193b872281bbfaa2955b959c1b7fc6267d0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8588888c7f3d743ff264ad594ec846b542ba18ab8c2476aafca0dcea41ac2a95(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2103c4d5bd9ccbc5b41fdf27bb786ac6712fa875bbea700976dd2bdc766349ed(
    value: typing.Optional[CertificateHttpChallenge],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__605409a4bee15f8b6bcfaf45521120d45150c389f7588057d7b80c1f42e2d9ae(
    *,
    hosts: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa59c1db9c06ff9e57cbe11bf896a4e29a4fdb1cd2420f69562316f8c7e0dad5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0ec37339e85235fb22702b24431cef78ae2af4e0e47fe72edfcd4fea1539201(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f992677746418c2fdc019ba79dfd620d731e02e4cc32b6f00a09fe2e276e61f3(
    value: typing.Optional[CertificateHttpMemcachedChallenge],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__340a44f2ee7e4ada999bb1cf87ccb90474c893a565d7bb31d7e8a45caf51acc0(
    *,
    s3_bucket: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddff2d15476435827bd344c64b14fddcf00c0fa634af4b25ee6d321da213a5a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0f65c84a2fc4338b7ac779a44580bc667f91417d85a5128777ed7b1a7134103(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9dd58b743326e186118958a66a6658b78d6b33630dd18f504b1f5e685d6aa8d(
    value: typing.Optional[CertificateHttpS3Challenge],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf8d6c9ec9e9ff59762c8dc206bc3e4982059675c841150c5ed60197eb5c1140(
    *,
    directory: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db3e907af81f5d87a81d1f1176f20cc00b50ecec623460f63c56d9a4474dd73c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6f75163fa53c0a6000c3c0c77235b9fceee7154df1f2b7cc53de5dfe42a6e06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__995b3fd1de1a09e12b5eef4fe62baf6b1eebb99a5ada9e3ac7e62ed00df2c59e(
    value: typing.Optional[CertificateHttpWebrootChallenge],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0a778adc41a2b38670f36d3b2542d792118b577dc80709ef033ca9ce3e12a19(
    *,
    port: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dddd1443cf652107dd160bf36fc4761ac7902b1745536601a8d27d93f398417a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19c18efa7592ff166fcd8a7237e29cdfbf6e494dc5b4b7f64fad8441b83291cc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__909933c29e9cbb8c06f132f102d101920ddd66b54c3a1dc16523ed12cd95acb9(
    value: typing.Optional[CertificateTlsChallenge],
) -> None:
    """Type checking stubs"""
    pass

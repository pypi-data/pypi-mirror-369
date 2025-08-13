r'''
# `acme_registration`

Refer to the Terraform Registry for docs: [`acme_registration`](https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration).
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


class Registration(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.registration.Registration",
):
    '''Represents a {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration acme_registration}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        email_address: builtins.str,
        account_key_algorithm: typing.Optional[builtins.str] = None,
        account_key_ecdsa_curve: typing.Optional[builtins.str] = None,
        account_key_pem: typing.Optional[builtins.str] = None,
        account_key_rsa_bits: typing.Optional[jsii.Number] = None,
        external_account_binding: typing.Optional[typing.Union["RegistrationExternalAccountBinding", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration acme_registration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param email_address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#email_address Registration#email_address}.
        :param account_key_algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_algorithm Registration#account_key_algorithm}.
        :param account_key_ecdsa_curve: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_ecdsa_curve Registration#account_key_ecdsa_curve}.
        :param account_key_pem: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_pem Registration#account_key_pem}.
        :param account_key_rsa_bits: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_rsa_bits Registration#account_key_rsa_bits}.
        :param external_account_binding: external_account_binding block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#external_account_binding Registration#external_account_binding}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#id Registration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c0693813ee17f6a1e8c9135cd851ea087fe076ebc14f2b9a3148aa2c368904a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RegistrationConfig(
            email_address=email_address,
            account_key_algorithm=account_key_algorithm,
            account_key_ecdsa_curve=account_key_ecdsa_curve,
            account_key_pem=account_key_pem,
            account_key_rsa_bits=account_key_rsa_bits,
            external_account_binding=external_account_binding,
            id=id,
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
        '''Generates CDKTF code for importing a Registration resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Registration to import.
        :param import_from_id: The id of the existing Registration that should be imported. Refer to the {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Registration to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0938fa1d3f0c1c0970bd467a39707904488ec03b2badc11d1ec11229dc7684b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putExternalAccountBinding")
    def put_external_account_binding(
        self,
        *,
        hmac_base64: builtins.str,
        key_id: builtins.str,
    ) -> None:
        '''
        :param hmac_base64: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#hmac_base64 Registration#hmac_base64}.
        :param key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#key_id Registration#key_id}.
        '''
        value = RegistrationExternalAccountBinding(
            hmac_base64=hmac_base64, key_id=key_id
        )

        return typing.cast(None, jsii.invoke(self, "putExternalAccountBinding", [value]))

    @jsii.member(jsii_name="resetAccountKeyAlgorithm")
    def reset_account_key_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountKeyAlgorithm", []))

    @jsii.member(jsii_name="resetAccountKeyEcdsaCurve")
    def reset_account_key_ecdsa_curve(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountKeyEcdsaCurve", []))

    @jsii.member(jsii_name="resetAccountKeyPem")
    def reset_account_key_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountKeyPem", []))

    @jsii.member(jsii_name="resetAccountKeyRsaBits")
    def reset_account_key_rsa_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountKeyRsaBits", []))

    @jsii.member(jsii_name="resetExternalAccountBinding")
    def reset_external_account_binding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalAccountBinding", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="externalAccountBinding")
    def external_account_binding(
        self,
    ) -> "RegistrationExternalAccountBindingOutputReference":
        return typing.cast("RegistrationExternalAccountBindingOutputReference", jsii.get(self, "externalAccountBinding"))

    @builtins.property
    @jsii.member(jsii_name="registrationUrl")
    def registration_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "registrationUrl"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyAlgorithmInput")
    def account_key_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountKeyAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyEcdsaCurveInput")
    def account_key_ecdsa_curve_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountKeyEcdsaCurveInput"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyPemInput")
    def account_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountKeyPemInput"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyRsaBitsInput")
    def account_key_rsa_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountKeyRsaBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="emailAddressInput")
    def email_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="externalAccountBindingInput")
    def external_account_binding_input(
        self,
    ) -> typing.Optional["RegistrationExternalAccountBinding"]:
        return typing.cast(typing.Optional["RegistrationExternalAccountBinding"], jsii.get(self, "externalAccountBindingInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyAlgorithm")
    def account_key_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountKeyAlgorithm"))

    @account_key_algorithm.setter
    def account_key_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f6abf2aff46497ca774159a1bfa4c67c6fb5fd005524dc2f844f82f26051521)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountKeyAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="accountKeyEcdsaCurve")
    def account_key_ecdsa_curve(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountKeyEcdsaCurve"))

    @account_key_ecdsa_curve.setter
    def account_key_ecdsa_curve(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bbdf07bdce7c58ae0efadd335d449971e63f166976112bd50d8ed6104f7941e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountKeyEcdsaCurve", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="accountKeyPem")
    def account_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountKeyPem"))

    @account_key_pem.setter
    def account_key_pem(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2044a9bb6ebeec721953b60e81a88f01b248ee9018195bf43d03e67301dc14be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountKeyPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="accountKeyRsaBits")
    def account_key_rsa_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountKeyRsaBits"))

    @account_key_rsa_bits.setter
    def account_key_rsa_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__659ce577ac21c59d5a55328919d5e219ad1dc30c44dc52d258b31a261919f2c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountKeyRsaBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailAddress")
    def email_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailAddress"))

    @email_address.setter
    def email_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd37adb4c1de38cdb035960d08577b808f81b34e9fca94a928a508d061994355)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49881d93b66c0352a60d394efa02471c1c079c7f7908c9a414953b2d49975af7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.registration.RegistrationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "email_address": "emailAddress",
        "account_key_algorithm": "accountKeyAlgorithm",
        "account_key_ecdsa_curve": "accountKeyEcdsaCurve",
        "account_key_pem": "accountKeyPem",
        "account_key_rsa_bits": "accountKeyRsaBits",
        "external_account_binding": "externalAccountBinding",
        "id": "id",
    },
)
class RegistrationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        email_address: builtins.str,
        account_key_algorithm: typing.Optional[builtins.str] = None,
        account_key_ecdsa_curve: typing.Optional[builtins.str] = None,
        account_key_pem: typing.Optional[builtins.str] = None,
        account_key_rsa_bits: typing.Optional[jsii.Number] = None,
        external_account_binding: typing.Optional[typing.Union["RegistrationExternalAccountBinding", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param email_address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#email_address Registration#email_address}.
        :param account_key_algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_algorithm Registration#account_key_algorithm}.
        :param account_key_ecdsa_curve: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_ecdsa_curve Registration#account_key_ecdsa_curve}.
        :param account_key_pem: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_pem Registration#account_key_pem}.
        :param account_key_rsa_bits: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_rsa_bits Registration#account_key_rsa_bits}.
        :param external_account_binding: external_account_binding block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#external_account_binding Registration#external_account_binding}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#id Registration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(external_account_binding, dict):
            external_account_binding = RegistrationExternalAccountBinding(**external_account_binding)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff8c2d74eb491191cfc5a0e8648b2b676fdb766bb010ab757dcb8cb2aa5daf13)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument email_address", value=email_address, expected_type=type_hints["email_address"])
            check_type(argname="argument account_key_algorithm", value=account_key_algorithm, expected_type=type_hints["account_key_algorithm"])
            check_type(argname="argument account_key_ecdsa_curve", value=account_key_ecdsa_curve, expected_type=type_hints["account_key_ecdsa_curve"])
            check_type(argname="argument account_key_pem", value=account_key_pem, expected_type=type_hints["account_key_pem"])
            check_type(argname="argument account_key_rsa_bits", value=account_key_rsa_bits, expected_type=type_hints["account_key_rsa_bits"])
            check_type(argname="argument external_account_binding", value=external_account_binding, expected_type=type_hints["external_account_binding"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email_address": email_address,
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
        if account_key_algorithm is not None:
            self._values["account_key_algorithm"] = account_key_algorithm
        if account_key_ecdsa_curve is not None:
            self._values["account_key_ecdsa_curve"] = account_key_ecdsa_curve
        if account_key_pem is not None:
            self._values["account_key_pem"] = account_key_pem
        if account_key_rsa_bits is not None:
            self._values["account_key_rsa_bits"] = account_key_rsa_bits
        if external_account_binding is not None:
            self._values["external_account_binding"] = external_account_binding
        if id is not None:
            self._values["id"] = id

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
    def email_address(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#email_address Registration#email_address}.'''
        result = self._values.get("email_address")
        assert result is not None, "Required property 'email_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_key_algorithm(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_algorithm Registration#account_key_algorithm}.'''
        result = self._values.get("account_key_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def account_key_ecdsa_curve(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_ecdsa_curve Registration#account_key_ecdsa_curve}.'''
        result = self._values.get("account_key_ecdsa_curve")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def account_key_pem(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_pem Registration#account_key_pem}.'''
        result = self._values.get("account_key_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def account_key_rsa_bits(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#account_key_rsa_bits Registration#account_key_rsa_bits}.'''
        result = self._values.get("account_key_rsa_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def external_account_binding(
        self,
    ) -> typing.Optional["RegistrationExternalAccountBinding"]:
        '''external_account_binding block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#external_account_binding Registration#external_account_binding}
        '''
        result = self._values.get("external_account_binding")
        return typing.cast(typing.Optional["RegistrationExternalAccountBinding"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#id Registration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistrationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.registration.RegistrationExternalAccountBinding",
    jsii_struct_bases=[],
    name_mapping={"hmac_base64": "hmacBase64", "key_id": "keyId"},
)
class RegistrationExternalAccountBinding:
    def __init__(self, *, hmac_base64: builtins.str, key_id: builtins.str) -> None:
        '''
        :param hmac_base64: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#hmac_base64 Registration#hmac_base64}.
        :param key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#key_id Registration#key_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4300eef9525fa2c5804a39935d4c4b093e6ccae4d7cfe9470deff9458f00e6c1)
            check_type(argname="argument hmac_base64", value=hmac_base64, expected_type=type_hints["hmac_base64"])
            check_type(argname="argument key_id", value=key_id, expected_type=type_hints["key_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hmac_base64": hmac_base64,
            "key_id": key_id,
        }

    @builtins.property
    def hmac_base64(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#hmac_base64 Registration#hmac_base64}.'''
        result = self._values.get("hmac_base64")
        assert result is not None, "Required property 'hmac_base64' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vancluever/acme/2.35.1/docs/resources/registration#key_id Registration#key_id}.'''
        result = self._values.get("key_id")
        assert result is not None, "Required property 'key_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistrationExternalAccountBinding(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RegistrationExternalAccountBindingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.registration.RegistrationExternalAccountBindingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__068641f0611b905a6b090689adf097243454ec4bbdddcddd81ef560b439a508b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="hmacBase64Input")
    def hmac_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hmacBase64Input"))

    @builtins.property
    @jsii.member(jsii_name="keyIdInput")
    def key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="hmacBase64")
    def hmac_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hmacBase64"))

    @hmac_base64.setter
    def hmac_base64(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97ebd45de4c449eae0d69296c5b9148c3ca186101215b8dd7f7e2cf459b131e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hmacBase64", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @key_id.setter
    def key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81a3eac67be3bf7f6a8e4edb04e44d9d5ae2c2e8879db07fc77f9da9453adfd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RegistrationExternalAccountBinding]:
        return typing.cast(typing.Optional[RegistrationExternalAccountBinding], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RegistrationExternalAccountBinding],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cf2491ab96ed2112bea07fadf6fd2406939ab0d2bb01885a986bb8c82c3d1c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Registration",
    "RegistrationConfig",
    "RegistrationExternalAccountBinding",
    "RegistrationExternalAccountBindingOutputReference",
]

publication.publish()

def _typecheckingstub__6c0693813ee17f6a1e8c9135cd851ea087fe076ebc14f2b9a3148aa2c368904a(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    email_address: builtins.str,
    account_key_algorithm: typing.Optional[builtins.str] = None,
    account_key_ecdsa_curve: typing.Optional[builtins.str] = None,
    account_key_pem: typing.Optional[builtins.str] = None,
    account_key_rsa_bits: typing.Optional[jsii.Number] = None,
    external_account_binding: typing.Optional[typing.Union[RegistrationExternalAccountBinding, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__c0938fa1d3f0c1c0970bd467a39707904488ec03b2badc11d1ec11229dc7684b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f6abf2aff46497ca774159a1bfa4c67c6fb5fd005524dc2f844f82f26051521(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bbdf07bdce7c58ae0efadd335d449971e63f166976112bd50d8ed6104f7941e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2044a9bb6ebeec721953b60e81a88f01b248ee9018195bf43d03e67301dc14be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__659ce577ac21c59d5a55328919d5e219ad1dc30c44dc52d258b31a261919f2c7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd37adb4c1de38cdb035960d08577b808f81b34e9fca94a928a508d061994355(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49881d93b66c0352a60d394efa02471c1c079c7f7908c9a414953b2d49975af7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff8c2d74eb491191cfc5a0e8648b2b676fdb766bb010ab757dcb8cb2aa5daf13(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    email_address: builtins.str,
    account_key_algorithm: typing.Optional[builtins.str] = None,
    account_key_ecdsa_curve: typing.Optional[builtins.str] = None,
    account_key_pem: typing.Optional[builtins.str] = None,
    account_key_rsa_bits: typing.Optional[jsii.Number] = None,
    external_account_binding: typing.Optional[typing.Union[RegistrationExternalAccountBinding, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4300eef9525fa2c5804a39935d4c4b093e6ccae4d7cfe9470deff9458f00e6c1(
    *,
    hmac_base64: builtins.str,
    key_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__068641f0611b905a6b090689adf097243454ec4bbdddcddd81ef560b439a508b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97ebd45de4c449eae0d69296c5b9148c3ca186101215b8dd7f7e2cf459b131e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81a3eac67be3bf7f6a8e4edb04e44d9d5ae2c2e8879db07fc77f9da9453adfd9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cf2491ab96ed2112bea07fadf6fd2406939ab0d2bb01885a986bb8c82c3d1c7(
    value: typing.Optional[RegistrationExternalAccountBinding],
) -> None:
    """Type checking stubs"""
    pass

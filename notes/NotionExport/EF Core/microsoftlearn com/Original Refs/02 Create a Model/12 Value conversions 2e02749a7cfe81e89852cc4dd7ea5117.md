# 12. Value conversions

# Value Conversions

Value converters allow property values to be converted when reading from or writing to the database. This conversion can be from one value to another of the same type (for example, encrypting strings) or from a value of one type to a value of another type (for example, converting enum values to and from strings in the database.)

<aside>
💡 **TIP:** You can run and debug into all the code in this document by[downloading the sample code from GitHub](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Modeling/ValueConversions/).

</aside>

## Overview

Value converters are specified in terms of a ModelClrType and a ProviderClrType. The model type is the .NET type of the property in the entity type. The provider type is the .NET type understood by the database provider. For example, to save enums as strings in the database, the model type is the type of the enum, and the provider type is String. These two types can be the same.

Conversions are defined using two Func expression trees: one from ModelClrType to ProviderClrType and the other from ProviderClrType to ModelClrType. Expression trees are used so that they can be compiled into the database access delegate for efficient conversions. The expression tree may contain a simple call to a conversion method for complex conversions.

<aside>
ℹ️ **NOTE:** A property that has been configured for value conversion may also need to specify a[ValueComparer](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.valuecomparer-1). See the examples below, and the[Value Comparers](https://learn.microsoft.com/en-us/ef/core/modeling/value-comparers)documentation for more information.

</aside>

## Configuring a value converter

Value conversions are configured in [DbContext.OnModelCreating](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.onmodelcreating). For example, consider an enum and entity type defined as:

```csharp
public class Rider
{
    public int Id { get; set; }
    public EquineBeast Mount { get; set; }
}

public enum EquineBeast
{
    Donkey,
    Mule,
    Horse,
    Unicorn
}

```

Conversions can be configured in [OnModelCreating](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.onmodelcreating) to store the enum values as strings such as "Donkey", "Mule", etc. in the database; you simply need to provide one function which converts from the ModelClrType to the ProviderClrType, and another for the opposite conversion:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder
        .Entity<Rider>()
        .Property(e => e.Mount)
        .HasConversion(
            v => v.ToString(),
            v => (EquineBeast)Enum.Parse(typeof(EquineBeast), v));
}

```

<aside>
ℹ️ **NOTE:** Anullvalue will never be passed to a value converter. A null in a database column is always a null in the entity instance, and vice-versa. This makes the implementation of conversions easier and allows them to be shared amongst nullable and non-nullable properties. See[GitHub issue #13850](https://github.com/dotnet/efcore/issues/13850)for more information.

</aside>

### Bulk-configuring a value converter

It's common for the same value converter to be configured for every property that uses the relevant CLR type. Rather than doing this manually for each property, you can use [pre-convention model configuration](https://learn.microsoft.com/en-us/ef/core/modeling/bulk-configuration#pre-convention-configuration) to do this once for your entire model. To do this, define your value converter as a class:

```csharp
public class CurrencyConverter : ValueConverter<Currency, decimal>
{
    public CurrencyConverter()
        : base(
            v => v.Amount,
            v => new Currency(v))
    {
    }
}

```

Then, override [ConfigureConventions](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.configureconventions) in your context type and configure the converter as follows:

```csharp
protected override void ConfigureConventions(ModelConfigurationBuilder configurationBuilder)
{
    configurationBuilder
        .Properties<Currency>()
        .HaveConversion<CurrencyConverter>();
}

```

## Pre-defined conversions

EF Core contains many pre-defined conversions that avoid the need to write conversion functions manually. Instead, EF Core will pick the conversion to use based on the property type in the model and the requested database provider type.

For example, enum to string conversions are used as an example above, but EF Core will actually do this automatically when the provider type is configured as string using the generic type of [HasConversion](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.propertybuilder.hasconversion):

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder
        .Entity<Rider>()
        .Property(e => e.Mount)
        .HasConversion<string>();
}

```

The same thing can be achieved by explicitly specifying the database column type. For example, if the entity type is defined like so:

### Data Annotations

```csharp
public class Rider2
{
    public int Id { get; set; }

    [Column(TypeName = "nvarchar(24)")]
    public EquineBeast Mount { get; set; }
}

```

### Fluent API

```csharp
modelBuilder
    .Entity<Rider2>()
    .Property(e => e.Mount)
    .HasColumnType("nvarchar(24)");

```

Then the enum values will be saved as strings in the database without any further configuration in [OnModelCreating](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.onmodelcreating).

## The ValueConverter class

Calling [HasConversion](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.propertybuilder.hasconversion) as shown above will create a [ValueConverter<TModel,TProvider>](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.valueconverter-2) instance and set it on the property. The ValueConverter can instead be created explicitly. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    var converter = new ValueConverter<EquineBeast, string>(
        v => v.ToString(),
        v => (EquineBeast)Enum.Parse(typeof(EquineBeast), v));

    modelBuilder
        .Entity<Rider>()
        .Property(e => e.Mount)
        .HasConversion(converter);
}

```

This can be useful when multiple properties use the same conversion.

## Built-in converters

As mentioned above, EF Core ships with a set of pre-defined [ValueConverter<TModel,TProvider>](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.valueconverter-2) classes, found in the [Microsoft.EntityFrameworkCore.Storage.ValueConversion](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion) namespace. In many cases EF will choose the appropriate built-in converter based on the type of the property in the model and the type requested in the database, as shown above for enums. For example, using .HasConversion() on a bool property will cause EF Core to convert bool values to numerical zero and one values:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder
        .Entity<User>()
        .Property(e => e.IsActive)
        .HasConversion<int>();
}

```

This is functionally the same as creating an instance of the built-in [BoolToZeroOneConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.booltozerooneconverter-1) and setting it explicitly:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    var converter = new BoolToZeroOneConverter<int>();

    modelBuilder
        .Entity<User>()
        .Property(e => e.IsActive)
        .HasConversion(converter);
}

```

The following table summarizes commonly-used pre-defined conversions from model/property types to database provider types. In the table any_numeric_type means one of int, short, long, byte, uint, ushort, ulong, sbyte, char, decimal, float, or double.

| Model/property type | Provider/database type | Conversion | Usage |
| --- | --- | --- | --- |
| bool | any_numeric_type | False/true to 0/1 | .HasConversion<any_numeric_type>() |
|  | any_numeric_type | False/true to any two numbers | Use[BoolToTwoValuesConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.booltotwovaluesconverter-1) |
|  | string | False/true to "N"/"Y" | .HasConversion() |
|  | string | False/true to any two strings | Use[BoolToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.booltostringconverter) |
| any_numeric_type | bool | 0/1 to false/true | .HasConversion() |
|  | any_numeric_type | Simple cast | .HasConversion<any_numeric_type>() |
|  | string | The number as a string | .HasConversion() |
| Enum | any_numeric_type | The numeric value of the enum | .HasConversion<any_numeric_type>() |
|  | string | The string representation of the enum value | .HasConversion() |
| string | bool | Parses the string as a bool | .HasConversion() |
|  | any_numeric_type | Parses the string as the given numeric type | .HasConversion<any_numeric_type>() |
|  | char | The first character of the string | .HasConversion() |
|  | DateTime | Parses the string as a DateTime | .HasConversion() |
|  | DateTimeOffset | Parses the string as a DateTimeOffset | .HasConversion() |
|  | TimeSpan | Parses the string as a TimeSpan | .HasConversion() |
|  | Guid | Parses the string as a Guid | .HasConversion() |
|  | byte[] | The string as UTF8 bytes | .HasConversion<byte[]>() |
| char | string | A single character string | .HasConversion() |
| DateTime | long | Encoded date/time preserving DateTime.Kind | .HasConversion() |
|  | long | Ticks | Use[DateTimeToTicksConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.datetimetoticksconverter) |
|  | string | Invariant culture date/time string | .HasConversion() |
| DateTimeOffset | long | Encoded date/time with offset | .HasConversion() |
|  | string | Invariant culture date/time string with offset | .HasConversion() |
| TimeSpan | long | Ticks | .HasConversion() |
|  | string | Invariant culture time span string | .HasConversion() |
| Uri | string | The URI as a string | .HasConversion() |
| PhysicalAddress | string | The address as a string | .HasConversion() |
|  | byte[] | Bytes in big-endian network order | .HasConversion<byte[]>() |
| IPAddress | string | The address as a string | .HasConversion() |
|  | byte[] | Bytes in big-endian network order | .HasConversion<byte[]>() |
| Guid | string | The GUID in 'dddddddd-dddd-dddd-dddd-dddddddddddd' format | .HasConversion() |
|  | byte[] | Bytes in .NET binary serialization order | .HasConversion<byte[]>() |

Note that these conversions assume that the format of the value is appropriate for the conversion. For example, converting strings to numbers will fail if the string values cannot be parsed as numbers.

The full list of built-in converters is:

- Converting bool properties:
- [BoolToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.booltostringconverter) - Bool to strings such as "N" and "Y"
- [BoolToTwoValuesConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.booltotwovaluesconverter-1) - Bool to any two values
- [BoolToZeroOneConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.booltozerooneconverter-1) - Bool to zero and one
- Converting byte array properties:
- [BytesToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.bytestostringconverter) - Byte array to Base64-encoded string
- Any conversion that requires only a type-cast
- [CastingConverter<TModel,TProvider>](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.castingconverter-2) - Conversions that require only a type cast
- Converting char properties:
- [CharToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.chartostringconverter) - Char to single character string
- Converting [DateTimeOffset](https://learn.microsoft.com/en-us/dotnet/api/system.datetimeoffset) properties:
- [DateTimeOffsetToBinaryConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.datetimeoffsettobinaryconverter) - [DateTimeOffset](https://learn.microsoft.com/en-us/dotnet/api/system.datetimeoffset) to binary-encoded 64-bit value
- [DateTimeOffsetToBytesConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.datetimeoffsettobytesconverter) - [DateTimeOffset](https://learn.microsoft.com/en-us/dotnet/api/system.datetimeoffset) to byte array
- [DateTimeOffsetToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.datetimeoffsettostringconverter) - [DateTimeOffset](https://learn.microsoft.com/en-us/dotnet/api/system.datetimeoffset) to string
- Converting [DateTime](https://learn.microsoft.com/en-us/dotnet/api/system.datetime) properties:
- [DateTimeToBinaryConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.datetimetobinaryconverter) - [DateTime](https://learn.microsoft.com/en-us/dotnet/api/system.datetime) to 64-bit value including DateTimeKind
- [DateTimeToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.datetimetostringconverter) - [DateTime](https://learn.microsoft.com/en-us/dotnet/api/system.datetime) to string
- [DateTimeToTicksConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.datetimetoticksconverter) - [DateTime](https://learn.microsoft.com/en-us/dotnet/api/system.datetime) to ticks
- Converting enum properties:
- [EnumToNumberConverter<TEnum,TNumber>](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.enumtonumberconverter-2) - Enum to underlying number
- [EnumToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.enumtostringconverter-1) - Enum to string
- Converting [Guid](https://learn.microsoft.com/en-us/dotnet/api/system.guid) properties:
- [GuidToBytesConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.guidtobytesconverter) - [Guid](https://learn.microsoft.com/en-us/dotnet/api/system.guid) to byte array
- [GuidToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.guidtostringconverter) - [Guid](https://learn.microsoft.com/en-us/dotnet/api/system.guid) to string
- Converting [IPAddress](https://learn.microsoft.com/en-us/dotnet/api/system.net.ipaddress) properties:
- [IPAddressToBytesConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.ipaddresstobytesconverter) - [IPAddress](https://learn.microsoft.com/en-us/dotnet/api/system.net.ipaddress) to byte array
- [IPAddressToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.ipaddresstostringconverter) - [IPAddress](https://learn.microsoft.com/en-us/dotnet/api/system.net.ipaddress) to string
- Converting numeric (int, double, decimal, etc.) properties:
- [NumberToBytesConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.numbertobytesconverter-1) - Any numerical value to byte array
- [NumberToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.numbertostringconverter-1) - Any numerical value to string
- Converting [PhysicalAddress](https://learn.microsoft.com/en-us/dotnet/api/system.net.networkinformation.physicaladdress) properties:
- [PhysicalAddressToBytesConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.physicaladdresstobytesconverter) - [PhysicalAddress](https://learn.microsoft.com/en-us/dotnet/api/system.net.networkinformation.physicaladdress) to byte array
- [PhysicalAddressToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.physicaladdresstostringconverter) - [PhysicalAddress](https://learn.microsoft.com/en-us/dotnet/api/system.net.networkinformation.physicaladdress) to string
- Converting string properties:
- [StringToBoolConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.stringtoboolconverter) - Strings such as "N" and "Y" to bool
- [StringToBytesConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.stringtobytesconverter) - String to UTF8 bytes
- [StringToCharConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.stringtocharconverter) - String to character
- [StringToDateTimeConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.stringtodatetimeconverter) - String to [DateTime](https://learn.microsoft.com/en-us/dotnet/api/system.datetime)
- [StringToDateTimeOffsetConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.stringtodatetimeoffsetconverter) - String to [DateTimeOffset](https://learn.microsoft.com/en-us/dotnet/api/system.datetimeoffset)
- [StringToEnumConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.stringtoenumconverter-1) - String to enum
- [StringToGuidConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.stringtoguidconverter) - String to [Guid](https://learn.microsoft.com/en-us/dotnet/api/system.guid)
- [StringToNumberConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.stringtonumberconverter-1) - String to numeric type
- [StringToTimeSpanConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.stringtotimespanconverter) - String to [TimeSpan](https://learn.microsoft.com/en-us/dotnet/api/system.timespan)
- [StringToUriConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.stringtouriconverter) - String to [Uri](https://learn.microsoft.com/en-us/dotnet/api/system.uri)
- Converting [TimeSpan](https://learn.microsoft.com/en-us/dotnet/api/system.timespan) properties:
- [TimeSpanToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.timespantostringconverter) - [TimeSpan](https://learn.microsoft.com/en-us/dotnet/api/system.timespan) to string
- [TimeSpanToTicksConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.timespantoticksconverter) - [TimeSpan](https://learn.microsoft.com/en-us/dotnet/api/system.timespan) to ticks
- Converting [Uri](https://learn.microsoft.com/en-us/dotnet/api/system.uri) properties:
- [UriToStringConverter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.valueconversion.uritostringconverter) - [Uri](https://learn.microsoft.com/en-us/dotnet/api/system.uri) to string

Note that all the built-in converters are stateless and so a single instance can be safely shared by multiple properties.

## Column facets and mapping hints

Some database types have facets that modify how the data is stored. These include:

- Precision and scale for decimals and date/time columns
- Size/length for binary and string columns
- Unicode for string columns

These facets can be configured in the normal way for a property that uses a value converter, and will apply to the converted database type. For example, when converting from an enum to strings, we can specify that the database column should be non-Unicode and store up to 20 characters:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder
        .Entity<Rider>()
        .Property(e => e.Mount)
        .HasConversion<string>()
        .HasMaxLength(20)
        .IsUnicode(false);
}

```

Or, when creating the converter explicitly:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    var converter = new ValueConverter<EquineBeast, string>(
        v => v.ToString(),
        v => (EquineBeast)Enum.Parse(typeof(EquineBeast), v));

    modelBuilder
        .Entity<Rider>()
        .Property(e => e.Mount)
        .HasConversion(converter)
        .HasMaxLength(20)
        .IsUnicode(false);
}

```
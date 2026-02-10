# 3. Microsoft.Extensions.Logging

# Using Microsoft.Extensions.Logging in EF Core

[Microsoft.Extensions.Logging](https://learn.microsoft.com/en-us/dotnet/core/extensions/logging) is an extensible logging mechanism with plug-in providers for many common logging systems. Both Microsoft-supplied plug-ins (e.g [Microsoft.Extensions.Logging.Console](https://www.nuget.org/packages/Microsoft.Extensions.Logging.Console/)) and third-party plug-ins (e.g. [Serilog.Extensions.Logging](https://www.nuget.org/packages/Serilog.Extensions.Logging/)) are available as NuGet packages.

Entity Framework Core (EF Core) fully integrates with Microsoft.Extensions.Logging. However, consider using [simple logging](https://learn.microsoft.com/en-us/ef/core/logging-events-diagnostics/simple-logging) for a simpler way to log, especially for applications that don't use dependency injection.

## ASP.NET Core applications

Microsoft.Extensions.Logging is [used by default in ASP.NET Core applications](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging). Calling [AddDbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.dependencyinjection.entityframeworkservicecollectionextensions.adddbcontext) or [AddDbContextPool](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.dependencyinjection.entityframeworkservicecollectionextensions.adddbcontextpool) makes EF Core automatically use the logging setup configured via the regular ASP.NET mechanism.

## Other application types

Other application types can use the [GenericHost](https://learn.microsoft.com/en-us/dotnet/core/extensions/generic-host) to get the same dependency injection patterns as are used in ASP.NET Core. [AddDbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.dependencyinjection.entityframeworkservicecollectionextensions.adddbcontext) or [AddDbContextPool](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.dependencyinjection.entityframeworkservicecollectionextensions.adddbcontextpool) can then be used just like in ASP.NET Core applications.

Microsoft.Extensions.Logging can also be used for applications that don't use dependency injection, although [simple logging](https://learn.microsoft.com/en-us/ef/core/logging-events-diagnostics/simple-logging) can be easier to set up.

Microsoft.Extensions.Logging requires creation of a [LoggerFactory](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.logging.loggerfactory). This factory should be stored as a static/global instance somewhere and used each time a DbContext is created. For example, it is common to store the logger factory as a static property on the DbContext.

```csharp
public static readonly ILoggerFactory MyLoggerFactory
    = LoggerFactory.Create(builder => { builder.AddConsole(); });

```

This singleton/global instance should then be registered with EF Core on the [DbContextOptionsBuilder](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontextoptionsbuilder). For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .UseLoggerFactory(MyLoggerFactory)
        .UseSqlServer(@"Server=(localdb)\mssqllocaldb;Database=EFLogging;Trusted_Connection=True;ConnectRetryCount=0");

```

## Getting detailed messages

<aside>
💡 **TIP:** OnConfiguring is still called when AddDbContext is used or a DbContextOptions instance is passed to the DbContext constructor. This makes it the ideal place to apply context configuration regardless of how the DbContext is constructed.

</aside>

### Sensitive data

By default, EF Core will not include the values of any data in exception messages. This is because such data may be confidential, and could be revealed in production use if an exception is not handled.

However, knowing data values, especially for keys, can be very helpful when debugging. This can be enabled in EF Core by calling [EnableSensitiveDataLogging()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontextoptionsbuilder.enablesensitivedatalogging#microsoft-entityframeworkcore-dbcontextoptionsbuilder-enablesensitivedatalogging). For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.EnableSensitiveDataLogging();

```

### Detailed query exceptions

For performance reasons, EF Core does not wrap each call to read a value from the database provider in a try-catch block. However, this sometimes results in exceptions that are hard to diagnose, especially when the database returns a NULL when not allowed by the model.

Turning on [EnableDetailedErrors](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontextoptionsbuilder.enabledetailederrors) will cause EF to introduce these try-catch blocks and thereby provide more detailed errors. For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.EnableDetailedErrors();

```

## Configuration for specific messages

The EF Core [ConfigureWarnings](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontextoptionsbuilder.configurewarnings) API allows applications to change what happens when a specific event is encountered. This can be used to:

- Change the log level at which the event is logged
- Skip logging the event altogether
- Throw an exception when the event occurs

### Changing the log level for an event

Sometimes it can be useful to change the pre-defined log level for an event. For example, this can be used to promote two additional events from LogLevel.Debug to LogLevel.Information:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .ConfigureWarnings(
            b => b.Log(
                (RelationalEventId.ConnectionOpened, LogLevel.Information),
                (RelationalEventId.ConnectionClosed, LogLevel.Information)));

```

### Suppress logging an event

In a similar way, an individual event can be suppressed from logging. This is particularly useful for ignoring a warning that has been reviewed and understood. For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .ConfigureWarnings(b => b.Ignore(CoreEventId.DetachedLazyLoadingWarning));

```

### Throw for an event

Finally, EF Core can be configured to throw for a given event. This is particularly useful for changing a warning into an error. (Indeed, this was the original purpose of ConfigureWarnings method, hence the name.) For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .ConfigureWarnings(b => b.Throw(RelationalEventId.QueryPossibleUnintendedUseOfEqualsWarning));

```

## Filtering and other configuration

See [Logging in .NET](https://learn.microsoft.com/en-us/dotnet/core/extensions/logging) for guidance on log filtering and other configuration.

EF Core logging events are defined in one of:

- [CoreEventId](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.coreeventid) for events common to all EF Core database providers
- [RelationalEventId](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.relationaleventid) for events common to all relational database providers
- A similar class for events specific to the current database provider. For example, [SqlServerEventId](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.sqlservereventid) for the SQL Server provider.

These definitions contain the event IDs, log level, and category for each event, as used by Microsoft.Extensions.Logging.
# 2. Simple logging

# Simple Logging

<aside>
💡 **TIP:** You can [download this article's sample](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Miscellaneous/Logging/SimpleLogging) from GitHub.

</aside>

Entity Framework Core (EF Core) simple logging can be used to easily obtain logs while developing and debugging applications. This form of logging requires minimal configuration and no additional NuGet packages.

<aside>
💡 **TIP:** EF Core also integrates with [Microsoft.Extensions.Logging](https://learn.microsoft.com/en-us/ef/core/logging-events-diagnostics/extensions-logging) , which requires more configuration, but is often more suitable for logging in production applications.

</aside>

## Configuration

EF Core logs can be accessed from any type of application through the use of [LogTo](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontextoptionsbuilder.logto) when [configuring a DbContext instance](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/). This configuration is commonly done in an override of [DbContext.OnConfiguring](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.onconfiguring). For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.LogTo(Console.WriteLine);

```

Alternately, LogTo can be called as part of [AddDbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.dependencyinjection.entityframeworkservicecollectionextensions.adddbcontext) or when creating a [DbContextOptions](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontextoptions) instance to pass to the DbContext constructor.

<aside>
💡 **TIP:** OnConfiguring is still called when AddDbContext is used or a DbContextOptions instance is passed to the DbContext constructor. This makes it the ideal place to apply context configuration regardless of how the DbContext is constructed.

</aside>

## Directing the logs

### Logging to the console

LogTo requires an [Action](https://learn.microsoft.com/en-us/dotnet/api/system.action-1) delegate that accepts a string. EF Core will call this delegate with a string for each log message generated. It is then up to the delegate to do something with the given message.

The [Console.WriteLine](https://learn.microsoft.com/en-us/dotnet/api/system.console.writeline) method is often used for this delegate, as shown above. This results in each log message being written to the console.

### Logging to the debug window

[Debug.WriteLine](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.debug.writeline) can be used to send output to the Debug window in Visual Studio or other IDEs. [Lambda syntax](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-expressions) must be used in this case because the Debug class is compiled out of release builds. For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.LogTo(message => Debug.WriteLine(message));

```

### Logging to a file

Writing to a file requires creating a [StreamWriter](https://learn.microsoft.com/en-us/dotnet/api/system.io.streamwriter) or similar for the file. The [WriteLine](https://learn.microsoft.com/en-us/dotnet/api/system.io.streamwriter.writeline) method can then be used as in the other examples above. Remember to ensure the file is closed cleanly by disposing the writer when the context is disposed. For example:

```csharp
private readonly StreamWriter _logStream = new StreamWriter("mylog.txt", append: true);

protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.LogTo(_logStream.WriteLine);

public override void Dispose()
{
    base.Dispose();
    _logStream.Dispose();
}

public override async ValueTask DisposeAsync()
{
    await base.DisposeAsync();
    await _logStream.DisposeAsync();
}

```

<aside>
💡 **TIP:** Consider using [Microsoft.Extensions.Logging](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging) for logging to files in production applications.

</aside>

## Getting detailed messages

### Sensitive data

By default, EF Core will not include the values of any data in exception messages. This is because such data may be confidential, and could be revealed in production use if an exception is not handled.

However, knowing data values, especially for keys, can be very helpful when debugging. This can be enabled in EF Core by calling [EnableSensitiveDataLogging()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontextoptionsbuilder.enablesensitivedatalogging#microsoft-entityframeworkcore-dbcontextoptionsbuilder-enablesensitivedatalogging). For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .LogTo(Console.WriteLine)
        .EnableSensitiveDataLogging();

```

### Detailed query exceptions

For performance reasons, EF Core does not wrap each call to read a value from the database provider in a try-catch block. However, this sometimes results in exceptions that are hard to diagnose, especially when the database returns a NULL when not allowed by the model.

Turning on [EnableDetailedErrors](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontextoptionsbuilder.enabledetailederrors) will cause EF to introduce these try-catch blocks and thereby provide more detailed errors. For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .LogTo(Console.WriteLine)
        .EnableDetailedErrors();

```

## Filtering

### Log levels

Every EF Core log message is assigned to a level defined by the [LogLevel](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.logging.loglevel) enum. By default, EF Core simple logging includes every message at Debug level or above. LogTo can be passed a higher minimum level to filter out some messages. For example, passing Information results in a minimal set of logs limited to database access and some housekeeping messages.

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.LogTo(Console.WriteLine, LogLevel.Information);

```

### Specific messages

Every log message is assigned an [EventId](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.logging.eventid). These IDs can be accessed from the [CoreEventId](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.coreeventid) class or the [RelationalEventId](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.relationaleventid) class for relational-specific messages. A database provider may also have provider-specific IDs in a similar class. For example, [SqlServerEventId](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.sqlservereventid) for the SQL Server provider.

LogTo can be configured to only log the messages associated with one or more event IDs. For example, to log only messages for the context being initialized or disposed:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .LogTo(Console.WriteLine, new[] { CoreEventId.ContextDisposed, CoreEventId.ContextInitialized });

```

### Message categories

Every log message is assigned to a named hierarchical logger category. The categories are:

| Category | Messages |
| --- | --- |
| Microsoft.EntityFrameworkCore | All EF Core messages |
| Microsoft.EntityFrameworkCore.Database | All database interactions |
| Microsoft.EntityFrameworkCore.Database.Connection | Uses of a database connection |
| Microsoft.EntityFrameworkCore.Database.Command | Uses of a database command |
| Microsoft.EntityFrameworkCore.Database.Transaction | Uses of a database transaction |
| Microsoft.EntityFrameworkCore.Update | Saving entities, excluding database interactions |
| Microsoft.EntityFrameworkCore.Model | All model and metadata interactions |
| Microsoft.EntityFrameworkCore.Model.Validation | Model validation |
| Microsoft.EntityFrameworkCore.Query | Queries, excluding database interactions |
| Microsoft.EntityFrameworkCore.Infrastructure | General events, such as context creation |
| Microsoft.EntityFrameworkCore.Scaffolding | Database reverse engineering |
| Microsoft.EntityFrameworkCore.Migrations | Migrations |
| Microsoft.EntityFrameworkCore.ChangeTracking | Change tracking interactions |

LogTo can be configured to only log the messages from one or more categories. For example, to log only database interactions:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .LogTo(Console.WriteLine, new[] { DbLoggerCategory.Database.Name });

```

Notice that the [DbLoggerCategory](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbloggercategory) class provides a hierarchical API for finding a category and avoids the need to hard-code strings.

Since categories are hierarchical, this example using the Database category will include all messages for the subcategories Database.Connection, Database.Command, and Database.Transaction.

### Custom filters

LogTo allows a custom filter to be used for cases where none of the filtering options above are sufficient. For example, to log any message at level Information or above, as well as messages for opening and closing a connection:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .LogTo(
            Console.WriteLine,
            (eventId, logLevel) => logLevel >= LogLevel.Information
                                   || eventId == RelationalEventId.ConnectionOpened
                                   || eventId == RelationalEventId.ConnectionClosed);

```

<aside>
💡 **TIP:** Filtering using custom filters or using any of the other options shown here is more efficient than filtering in the LogTo delegate. This is because if the filter determines the message should not be logged, then the log message is not even created.

</aside>

## Configuration for specific messages

The EF Core [ConfigureWarnings](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontextoptionsbuilder.configurewarnings) API allows applications to change what happens when a specific event is encountered. This can be used to:

- Change the log level at which the event is logged
- Skip logging the event altogether
- Throw an exception when the event occurs

### Changing the log level for an event

The previous example used a custom filter to log every message at LogLevel.Information as well as two events defined for LogLevel.Debug. The same can be achieved by changing the log level of the two Debug events to Information:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .ConfigureWarnings(
            b => b.Log(
                (RelationalEventId.ConnectionOpened, LogLevel.Information),
                (RelationalEventId.ConnectionClosed, LogLevel.Information)))
        .LogTo(Console.WriteLine, LogLevel.Information);

```

### Suppress logging an event

In a similar way, an individual event can be suppressed from logging. This is particularly useful for ignoring a warning that has been reviewed and understood. For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .ConfigureWarnings(b => b.Ignore(CoreEventId.DetachedLazyLoadingWarning))
        .LogTo(Console.WriteLine);

```

### Throw for an event

Finally, EF Core can be configured to throw for a given event. This is particularly useful for changing a warning into an error. (Indeed, this was the original purpose of ConfigureWarnings method, hence the name.) For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .ConfigureWarnings(b => b.Throw(RelationalEventId.MultipleCollectionIncludeWarning))
        .LogTo(Console.WriteLine);

```

## Message contents and formatting

The default content from LogTo is formatted across multiple lines. The first line contains message metadata:

- The [LogLevel](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.logging.loglevel) as a four-character prefix
- A local timestamp, formatted for the current culture
- The [EventId](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.logging.eventid) in the form that can be copy/pasted to get the member from [CoreEventId](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.coreeventid) or one of the other EventId classes, plus the raw ID value
- The event category, as described above.

For example:

```bash
info: 10/6/2020 10:52:45.581 RelationalEventId.CommandExecuted[20101] (Microsoft.EntityFrameworkCore.Database.Command)
      Executed DbCommand (0ms) [Parameters=[], CommandType='Text', CommandTimeout='30']
      CREATE TABLE "Blogs" (
          "Id" INTEGER NOT NULL CONSTRAINT "PK_Blogs" PRIMARY KEY AUTOINCREMENT,
          "Name" INTEGER NOT NULL
      );
dbug: 10/6/2020 10:52:45.582 RelationalEventId.TransactionCommitting[20210] (Microsoft.EntityFrameworkCore.Database.Transaction)
      Committing transaction.
dbug: 10/6/2020 10:52:45.585 RelationalEventId.TransactionCommitted[20202] (Microsoft.EntityFrameworkCore.Database.Transaction)
      Committed transaction.

```

This content can be customized by passing values from [DbContextLoggerOptions](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.dbcontextloggeroptions), as shown in the following sections.

<aside>
💡 **TIP:** Consider using [Microsoft.Extensions.Logging](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging) for more control over log formatting.

</aside>

### Using UTC time

By default, timestamps are designed for local consumption while debugging. Use [DbContextLoggerOptions.DefaultWithUtcTime](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.dbcontextloggeroptions#microsoft-entityframeworkcore-diagnostics-dbcontextloggeroptions-defaultwithutctime) to use culture-agnostic UTC timestamps instead, but keep everything else the same. For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.LogTo(
        Console.WriteLine,
        LogLevel.Debug,
        DbContextLoggerOptions.DefaultWithUtcTime);

```

This example results in the following log formatting:

```bash
info: 2020-10-06T17:55:39.0333701Z RelationalEventId.CommandExecuted[20101] (Microsoft.EntityFrameworkCore.Database.Command)
      Executed DbCommand (0ms) [Parameters=[], CommandType='Text', CommandTimeout='30']
      CREATE TABLE "Blogs" (
          "Id" INTEGER NOT NULL CONSTRAINT "PK_Blogs" PRIMARY KEY AUTOINCREMENT,
          "Name" INTEGER NOT NULL
      );
dbug: 2020-10-06T17:55:39.0333892Z RelationalEventId.TransactionCommitting[20210] (Microsoft.EntityFrameworkCore.Database.Transaction)
      Committing transaction.
dbug: 2020-10-06T17:55:39.0351684Z RelationalEventId.TransactionCommitted[20202] (Microsoft.EntityFrameworkCore.Database.Transaction)
      Committed transaction.

```

### Single line logging

Sometimes it is useful to get exactly one line per log message. This can be enabled by [DbContextLoggerOptions.SingleLine](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.dbcontextloggeroptions#microsoft-entityframeworkcore-diagnostics-dbcontextloggeroptions-singleline). For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.LogTo(
        Console.WriteLine,
        LogLevel.Debug,
        DbContextLoggerOptions.DefaultWithLocalTime | DbContextLoggerOptions.SingleLine);

```

This example results in the following log formatting:

```bash
info: 10/6/2020 10:52:45.723 RelationalEventId.CommandExecuted[20101] (Microsoft.EntityFrameworkCore.Database.Command) -> Executed DbCommand (0ms) [Parameters=[], CommandType='Text', CommandTimeout='30']CREATE TABLE "Blogs" (    "Id" INTEGER NOT NULL CONSTRAINT "PK_Blogs" PRIMARY KEY AUTOINCREMENT,    "Name" INTEGER NOT NULL);
dbug: 10/6/2020 10:52:45.723 RelationalEventId.TransactionCommitting[20210] (Microsoft.EntityFrameworkCore.Database.Transaction) -> Committing transaction.
dbug: 10/6/2020 10:52:45.725 RelationalEventId.TransactionCommitted[20202] (Microsoft.EntityFrameworkCore.Database.Transaction) -> Committed transaction.

```

### Other content options

Other flags in [DbContextLoggerOptions](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.diagnostics.dbcontextloggeroptions) can be used to trim down the amount of metadata included in the log. This can be useful in conjunction with single-line logging. For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.LogTo(
        Console.WriteLine,
        LogLevel.Debug,
        DbContextLoggerOptions.UtcTime | DbContextLoggerOptions.SingleLine);

```

This example results in the following log formatting:

```bash
2020-10-06T17:52:45.7320362Z -> Executed DbCommand (0ms) [Parameters=[], CommandType='Text', CommandTimeout='30']CREATE TABLE "Blogs" (    "Id" INTEGER NOT NULL CONSTRAINT "PK_Blogs" PRIMARY KEY AUTOINCREMENT,    "Name" INTEGER NOT NULL);
2020-10-06T17:52:45.7320531Z -> Committing transaction.
2020-10-06T17:52:45.7339441Z -> Committed transaction.

```

## Moving from EF6

EF Core simple logging differs from [Database.Log](https://learn.microsoft.com/en-us/dotnet/api/system.data.entity.database.log#system-data-entity-database-log) in EF6 in two important ways:

- Log messages are not limited to only database interactions
- The logging must be configured at context initialization time

For the first difference, the filtering described above can be used to limit which messages are logged.

The second difference is an intentional change to improve performance by not generating log messages when they are not needed. However, it is still possible to get a similar behavior to EF6 by creating a Log property on your DbContext and then using it only when it has been set. For example:

```csharp
public Action<string> Log { get; set; }

protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.LogTo(s => Log?.Invoke(s));

```
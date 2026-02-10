# 19. Spatial data

# Spatial Data

Spatial data represents physical locations and the shapes of objects. EF Core supports mapping these to spatial database types using the **NetTopologySuite (NTS)** library.

## 1. Installation

You must install the NTS extension package for your specific database provider.

| Provider | NuGet Package |
| --- | --- |
| **SQL Server** | `Microsoft.EntityFrameworkCore.SqlServer.NetTopologySuite` |
| **SQLite** | `Microsoft.EntityFrameworkCore.Sqlite.NetTopologySuite` |
| **PostgreSQL** | `Npgsql.EntityFrameworkCore.PostgreSQL.NetTopologySuite` |
| **MySQL** | `Pomelo.EntityFrameworkCore.MySql.NetTopologySuite` |

## 2. Configuration

Enable spatial support by calling `UseNetTopologySuite()` in your `DbContext` options configuration.

```csharp
options.UseSqlServer(connectionString, x => x.UseNetTopologySuite());

```

## 3. Mapping and Usage

EF Core maps NTS types (from `NetTopologySuite.Geometries`) to database spatial types.

### Common Types

- `Point`: A single location (X/Y).
- `LineString`: A path of points.
- `Polygon`: A closed shape.
- `Geometry`: Base type (allows any shape).

### Example: City Location

```csharp
public class City
{
    public int Id { get; set; }
    public string Name { get; set; }
    public Point Location { get; set; } // Uses NetTopologySuite.Geometries.Point
}

```

<aside>
🔥 **Coordinate Order:** NTS uses **X** for Longitude and **Y** for Latitude. This is the reverse of the common (Latitude, Longitude) format.

</aside>

## 4. Querying

NTS methods and properties are translated to server-side SQL spatial functions.

```csharp
// 1. Find the nearest city
var nearestCity = await db.Cities
    .OrderBy(c => c.Location.Distance(currentLocation))
    .FirstOrDefaultAsync();

// 2. Find if a location is inside a polygon (e.g., a country border)
var currentCountry = await db.Countries
    .FirstOrDefaultAsync(c => c.Border.Contains(currentLocation));

```

## 5. SRID and Projections

- **SRID (Spatial Reference ID):** 4326 (WGS 84) is the standard for GPS/web maps.
- **Client vs. Server:**
- **Client-evaluated** operations (in C#) treated as planar by NTS. For accurate distance calculations in meters on the client, you must project coordinates using a library like `ProjNet`.

## 6. Summary

- **Library:** Always use `NetTopologySuite`.
- **Translation:** Most spatial methods like `Distance`, `Intersects`, `Buffer`, and `Contains` are translated to SQL.
- **Performance:** Spatial columns should be indexed in the database (e.g., using `SPATIAL INDEX` in SQL Server).
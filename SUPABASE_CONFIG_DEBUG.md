# 🔍 DEBUG CONFIGURATION SUPABASE

## Informations récupérées

- **Project ID**: pzzfqduntcmklrakhggy
- **Région**: aws-1-eu-west-1 (Irlande)
- **Port**: 6543 (Transaction Pooler)
- **Mot de passe**: NyaYU8AHuzkRM9gh

## Erreur rencontrée

```
FATAL: password authentication failed for user "postgres"
FATAL: SSL connection is required
```

## Solutions à tester

### Format 1: Transaction Pooler avec SSL (actuel)
```
postgresql://postgres.pzzfqduntcmklrakhggy:NyaYU8AHuzkRM9gh@aws-1-eu-west-1.pooler.supabase.com:6543/postgres?sslmode=require
```

### Format 2: Direct Connection (Port 5432)
```
postgresql://postgres.pzzfqduntcmklrakhggy:NyaYU8AHuzkRM9gh@aws-1-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=require
```

### Format 3: Session Pooler (Port 6543 avec pgbouncer)
```
postgresql://postgres:NyaYU8AHuzkRM9gh@aws-1-eu-west-1.pooler.supabase.com:6543/postgres?sslmode=require&pgbouncer=true
```

## Actions à faire

1. Vérifier sur Supabase Dashboard:
   - Project Settings > Database > Connection String
   - Onglet "URI" 
   - Cocher "Use connection pooling"
   - Copier l'URL exacte

2. Vérifier que le mot de passe est bien celui configuré (pas celui par défaut)

3. Vérifier que la base de données "postgres" existe bien

## Note importante

Le Transaction Pooler (port 6543) utilise PgBouncer en mode "transaction". 
Pour Serverless (Vercel), c'est le bon choix.
Pour du développement local, le port 5432 (Direct Connection) peut être plus stable.


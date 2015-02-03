#!/bin/sh

FOLDING_HOME=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Create random passwords for two users

# folding user password. This user will have all privileges and will own the db.
# Any maintenance or backend activity should be done by him
openssl rand -base64 33 > passwords.txt; # folding user

# folding_web user password. Basically only read permission. Used by the web frontend.
# All third party activity must be done by him, never by the folding user
openssl rand -base64 33 >> passwords.txt; # folding_web user

# Add the long random password to the .pgpass file to avoid typing it
# If this script is run more than once
# the previously added .pgpass credentials line must be manually removed first
# otherwise there will be more than one line for the same db:user
# The credentials will be added to the .pgpass file of the user running the script
echo "localhost:*:folding:folding:"$(cat passwords.txt | head -n 1) >> $HOME/.pgpass
# If the .pgpass permission is not 0600 the psql client will ignore it
chmod 0600 $HOME/.pgpass

# This will create the users and the db
# The postgres user password will be asked for if it is not in the .pgpass file
psql -e -U postgres -f create_database.psql

# These will set the permissions on the web app directory
# The user running the scrip will own the tree
# Notice that the group must be set to the apache user
find $FOLDING_HOME"/kakaostats.com" -type d -print0 | xargs -0 chmod 2750
find $FOLDING_HOME"/kakaostats.com" -type f -print0 | xargs -0 chmod 0640
find $FOLDING_HOME"/kakaostats.com/static" -type d -print0 | xargs -0 chmod 2751
find $FOLDING_HOME"/kakaostats.com/static" -type f -print0 | xargs -0 chmod 0644
chown -R ${USER}:apache $FOLDING_HOME"/kakaostats.com"
